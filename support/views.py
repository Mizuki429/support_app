import os
from openai import OpenAI
from django.shortcuts import render, redirect
from django.core.management import call_command
from django.http import HttpResponse
from django.contrib import messages
from dotenv import load_dotenv
from .forms import ConcernForm
from .forms import SceneConfirmationForm
from .forms import StrategyForm
from .forms import SupportNeedForm
from .forms import IdealLifeForm
from django.http import HttpResponse

load_dotenv()

#最初に何に困っているかを聞いたあと、AIに裏で問い合わせる
# OpenRouter API クライアント初期化
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def ask_concern(request):
    suggestion = None

    if request.method == "POST":
        form = ConcernForm(request.POST)
        if form.is_valid():
            concern_text = form.cleaned_data["text"]
            request.session["concern"] = concern_text

            # プロンプトの作成
            prompt = (
                f"ユーザーは「{concern_text}」と困っているようです。"
                "この内容から、どのような日常生活の場面で特に困っていそうか、推測してください。"
                "このあと、場面別に困りごとの深掘りをします。"
                "やさしい語り口で、共感を示しながら、1〜2の具体的な場面を挙げてください。"
            )

            try:
                response = client.chat.completions.create(
                    model="mistralai/mistral-7b-instruct",  # 必要に応じて他モデルに変更可能
                    messages=[
                        {"role": "system", "content": "あなたは共感的なアシスタントです。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.7,
                )

                suggestion = response.choices[0].message.content.strip()
                request.session["scene_suggestion"] = suggestion
                return redirect("confirm_scene")

            except Exception as e:
                print("OpenRouter API error:", e)
                suggestion = "AIからの応答取得に失敗しました。"

    else:
        form = ConcernForm()

    return render(request, "support/ask_concern.html", {
        "form": form,
        "suggestion": suggestion
    })

#AIで問い合わせた場面をもとに質問を掘り下げる
def confirm_scene(request):
    suggestion = request.session.get("suggestion", "")

    if not suggestion:
        messages.warning(request, "AIの推測結果が見つかりませんでした。もう一度入力してください。")
        return redirect("ask_concern")

    if request.method == "POST":
        form = SceneConfirmationForm(request.POST)
        if form.is_valid():
            detail = form.cleaned_data["detail"]
            request.session["scene_detail"] = detail
            return redirect("ask_custom_strategy")
    else:
        form = SceneConfirmationForm()

    return render(request, "support/confirm_scene.html", {
        "suggestion": suggestion,
        "form": form
    })

#自分なりの対策方法を聞く
def ask_custom_strategy(request):
    if request.method == "POST":
        form = StrategyForm(request.POST)
        if form.is_valid():
            strategy = form.cleaned_data["strategy"]
            request.session["strategy"] = strategy
            return redirect("ask_support")
    else:
        form = StrategyForm()

    return render(request, "support/ask_strategy.html", {"form": form})

#どんなサポートがあれば良さそうか聞く
def ask_support(request):
    if request.method == "POST":
        form = SupportNeedForm(request.POST)
        if form.is_valid():
            support = form.cleaned_data["support"]
            request.session["support"] = support
            return redirect("ask_ideal")
    else:
        form = SupportNeedForm()

    return render(request, "support/ask_support.html", {"form": form})

#理想の生活を聞く
def ask_ideal(request):
    if request.method == "POST":
        form = IdealLifeForm(request.POST)
        if form.is_valid():
            ideal = form.cleaned_data["ideal"]
            request.session["ideal"] = ideal
            return redirect("summary")
    else:
        form = IdealLifeForm()

    return render(request, "support/ask_ideal.html", {"form": form})

#まとめ
def summary(request):
    from openai import OpenAI

    client = OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1"
    )

    # セッションからユーザー入力を取得
    concern = request.session.get("concern", "")
    strategy = request.session.get("custom_strategy", "")
    support = request.session.get("support_need", "")
    ideal = request.session.get("ideal", "")

    # AIへのプロンプト作成
    prompt = (
        "以下の内容は、あるユーザーが抱えている困りごとや工夫、希望する支援についての情報です。\n\n"
        f"困っていること: {concern}\n"
        f"本人が工夫していること: {strategy}\n"
        f"あったら嬉しい支援: {support}\n"
        f"理想の暮らし・働き方: {ideal}\n\n"
        "これらの情報をもとに、このユーザーにとって今後どのような支援が役立ちそうか、やさしい語り口で提案してください。"
    )

    try:
        response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",  # ClaudeやGPTに変えることも可
            messages=[
                {"role": "system", "content": "あなたは福祉の専門家のような優しく思いやりのあるアシスタントです。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
        )

        suggestion_summary = response.choices[0].message.content.strip()

    except Exception as e:
        print("OpenRouter summary API error:", e)
        suggestion_summary = "AIからのまとめ提案の取得に失敗しました。"

    return render(request, "support/summary.html", {
        "summary": suggestion_summary,
        "concern": concern,
        "scene": scene,
        "strategy": strategy,
        "support": support,
        "ideal": ideal,
    })

