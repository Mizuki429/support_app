from django import forms

class ConcernForm(forms.Form):
    text = forms.CharField(
        label="あなたの日常での困りごとはなんですか？",
        widget=forms.Textarea(attrs={"placeholder": "例：毎日気分が沈んでしまって、何もやる気が出ません"}),
        max_length=1000
    )

class SceneConfirmationForm(forms.Form):
    detail = forms.CharField(
        label="こういう場面で特に困っていることがあれば詳しく教えてください",
        widget=forms.Textarea(attrs={"placeholder": "例：朝どうしても起きられなくて遅刻してしまう"}),
        max_length=1000,
        required=False
    )

class StrategyForm(forms.Form):
    strategy = forms.CharField(
        label="あなたが自分なりに工夫していることがあれば教えてください",
        widget=forms.Textarea(attrs={"placeholder": "例：無理をしないために昼寝を取り入れている"}),
        max_length=1000,
        required=False
    )

class SupportNeedForm(forms.Form):
    support = forms.CharField(
        label="どんなサポートや配慮があれば、もう少し楽になりそうですか？",
        widget=forms.Textarea(attrs={
            "placeholder": "例：在宅勤務ができると助かります／朝はゆっくり始めたい　など"
        }),
        max_length=1000,
        required=False
    )


class IdealLifeForm(forms.Form):
    ideal = forms.CharField(
        label="あなたにとって理想の暮らしや働き方って、どんな感じですか？",
        widget=forms.Textarea(attrs={
            "placeholder": "例：週3日、1日4時間くらいのリモートワークで、余裕をもって過ごせる生活が理想です"
        }),
        max_length=1000,
        required=False
    )

