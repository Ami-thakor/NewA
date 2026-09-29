from django.db import models


class Voice(models.Model):
    name = models.CharField(max_length=100)
    reference_audio = models.FileField(upload_to="voices/")
    model = models.CharField(max_length=50, default="chatterbox")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Generation(models.Model):
    voice = models.ForeignKey(
        Voice,
        on_delete=models.CASCADE,
        related_name="generations"
    )

    text = models.TextField()
    model = models.CharField(max_length=50, default="chatterbox")
    language = models.CharField(max_length=20, default="hi")
    seed = models.IntegerField(default=12)
    pace = models.FloatField(default=1.0)

    output_audio = models.FileField(
        upload_to="outputs/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.voice.name} - {self.created_at}"