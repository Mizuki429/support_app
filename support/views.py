import os
import requests
from openai import OpenAI
from django.shortcuts import render, redirect
from django.core.management import call_command
from django.http import HttpResponse
from dotenv import load_dotenv
from .forms import ConcernForm
from .forms import SceneConfirmationForm
from .forms import StrategyForm
from .forms import SupportNeedForm
from .forms import IdealLifeForm
from django.http import HttpResponse

load_dotenv()
ai_API="https://api-inference.huggingface.co/models/AliiaR/DialoGPT-medium-empathetic-dialogues"

#最初に何に困っているかを聞いたあと、AIに裏で問い合わせる
def ask_concern(request):
    suggestion = None
    if request.method == "POST":
        form = ConcernForm(request.POST)
        if form.is_valid():
            concern_text = form.cleaned_data["text"]
            request.session["concern"] = concern_text
            hf_api_key = os.getenv("HUGGINGFACE_API_KEY")	
# --- AIに裏で問い合わせる ---
            headers = {
                "Authorization": f"Bearer {hf_api_key}"
            }

            prompt = (
                f"ユーザーは「{concern_text}」と困っているようです。この内容から、どのような日常生活の場面で特に困っていそうか、推測してください。このあと、場面別に困りごとの深堀をします。やさしい語り口で、共感を示しながら、1〜2の具体的な場面を挙げてください。\nAI:"
            )
            payload = {"inputs":prompt}

            response = requests.post(
                ai_API,
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                suggestion = result[0]["generated_text"] if isinstance(result, list) else result
                request.session["scene_suggestion"] = suggestion
                return redirect("confirm_scene")
            else:
                suggestion = "AIからの応答取得に失敗しました。"

    else:
        form = ConcernForm()
    print(suggestion)
    return render(request, "support/ask_concern.html", {
        "form": form,
        "suggestion": suggestion
    })

#AIで問い合わせた場面をもとに質問を掘り下げる
def confirm_scene(request):
    suggestion = request.session.get("suggestion", "")

    if not suggestion:
        messages.warning(request, "message": "AIの推測結果が見つかりませんでした。もう一度入力してください。")
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
    concern = request.session.get("concern", "")
    scene_suggestion = request.session.get("scene_suggestion", "")
    custom_strategy = request.session.get("custom_strategy", "")
    support_need = request.session.get("support_need", "")
    ideal = request.session.get("ideal", "")

    # AI用プロンプトを組み立て
    prompt = (
        "あなたはユーザーの困りごとを理解し、必要なサポートや提案を共感的に伝えるカウンセラーです。\n"
        "以下の内容をもとに、ユーザーに向けて優しく温かいアドバイスとまとめを書いてください。\n\n"
        f"■困っていること:\n{concern}\n\n"
        f"■AIが推測した困っていそうな場面:\n{scene_suggestion}\n\n"
        f"■自分なりの工夫:\n{custom_strategy}\n\n"
        f"■必要なサポート:\n{support_need}\n\n"
        f"■理想の暮らし・働き方:\n{ideal}\n\n"
        "【まとめと提案】"
    )

    hf_api_key = os.getenv("HF_API_KEY")
    if not hf_api_key:
        raise Exception("❌ Hugging Face APIキーが設定されていません。")

    headers = {
        "Authorization": f"Bearer {hf_api_key}"
    }

    payload = {
        "inputs": prompt
    }

    response = requests.post(
        ai_API,
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        result = response.json()
        ai_summary = result[0]["generated_text"] if isinstance(result, list) else result
    else:
        ai_summary = "AIからの応答取得に失敗しました。"

    return render(request, "support/summary.html", {
        "concern": concern,
        "scene_suggestion": scene_suggestion,
        "custom_strategy": custom_strategy,
        "support_need": support_need,
        "ideal": ideal,
        "ai_summary": ai_summary
    })

