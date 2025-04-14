from openai import OpenAI
import os
from django.shortcuts import render, redirect
from dotenv import load_dotenv
from .forms import ConcernForm
from .forms import SceneConfirmationForm
from .forms import StrategyForm
from .forms import SupportNeedForm
from .forms import IdealLifeForm

load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

#最初に何に困っているかを聞いたあと、AIに裏で問い合わせる
def ask_concern(request):
    if request.method == "POST":
        form = ConcernForm(request.POST)
        if form.is_valid():
            concern_text = form.cleaned_data["text"]
            request.session["concern"] = concern_text

# --- AIに裏で問い合わせる ---
            prompt = f"""
ユーザーは「{concern_text}」と困っているようです。
この内容から、どのような日常生活の場面で特に困っていそうか、推測してください。
このあと、場面別に困りごとの深堀をします。
やさしい語り口で、共感を示しながら、1〜2の具体的な場面を挙げてください。
"""

            response = client.chat.completions.create(
                model="anthropic/claude-3-haiku",
                messages=[
                    {"role": "system", "content": "あなたは共感的でやさしいカウンセラーです。"},
                    {"role": "user", "content": prompt}
                ]
            )

            suggestion = response.choices[0].message.content
            request.session["suggestion"] = suggestion

            return redirect("confirm_scene")
    else:
        form = ConcernForm()
    return render(request, "support/ask_concern.html", {"form": form})

#AIで問い合わせた場面をもとに質問を掘り下げる
def confirm_scene(request):
    suggestion = request.session.get("suggestion", "")

    if not suggestion:
        return render(request, "support/error.html", {"message": "AIの推測結果が見つかりません"})

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
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def summary(request):
    concern = request.session.get("concern", "")
    scene_detail = request.session.get("scene_detail", "")
    strategy = request.session.get("strategy", "")
    support = request.session.get("support", "")
    ideal = request.session.get("ideal", "")

    # --- AIに提案をお願いするためのプロンプトを生成 ---
    prompt = f"""
ユーザーは次のような困りごとや希望を話しています：

【困っていること】{concern}
【本人の補足】{scene_detail}
【工夫していること】{strategy}
【欲しいサポート】{support}
【理想の暮らし】{ideal}

この情報をもとに、ユーザーにとってどんなサポートや考え方が役立つか、
やさしく、丁寧に、1〜3つの提案をしてください。
できるだけ安心できる言葉で語りかけるようにお願いします。
"""

    try:
        response = client.chat.completions.create(
            model="anthropic/claude-3-haiku",
            messages=[
                {"role": "system", "content": "あなたは共感的で、やさしく思いやりのあるカウンセラーです。"},
                {"role": "user", "content": prompt}
            ]
        )
        ai_response = response.choices[0].message.content
    except Exception as e:
        ai_response = f"AIからの提案の取得に失敗しました：{str(e)}"

    context = {
        "concern": concern,
        "scene_detail": scene_detail,
        "strategy": strategy,
        "support": support,
        "ideal": ideal,
        "ai_response": ai_response,
    }

    return render(request, "support/summary.html", context)
