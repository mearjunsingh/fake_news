import re
import string
import joblib

from pathlib import Path

from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from datetime import datetime

from .utils import generate_unique_slug


def wordppt(text):
    text = text.lower()
    text = re.sub("\[.*?\]", "", text)
    text = re.sub("\\W", " ", text)
    text = re.sub("https?://\S+|www\.\S+", "", text)
    text = re.sub("<.*?>+", "", text)
    text = re.sub("[%s]" % re.escape(string.punctuation), "", text)
    text = re.sub("\n", "", text)
    text = re.sub("\w*\d\w*", "", text)
    return text


class Category(models.Model):
    name = models.CharField(max_length=55)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Blog(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, db_index=True)
    description = models.CharField(max_length=160)
    photo_main = models.ImageField(upload_to="uploads/%Y/%m")
    slug = models.SlugField(max_length=200, unique=True, editable=False)
    content = models.TextField()
    views = models.IntegerField(default=0)
    list_date = models.DateTimeField(default=datetime.now)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-list_date"]

    def __str__(self):
        return self.title

    def clean(self):
        BASE_DIR = Path(__file__).resolve().parent.parent

        LR = joblib.load(BASE_DIR / "backend/algorithm/lr.joblib")
        vectorization = joblib.load(BASE_DIR / "backend/algorithm/vectorization.joblib")

        text_cleaned = wordppt(self.content)
        new_x_test = [text_cleaned]
        new_xv_test = vectorization.transform(new_x_test)

        pred_LR = LR.predict(new_xv_test)

        if pred_LR[0] == 0:
            raise ValidationError("Fake news found")

    def save(self, *args, **kwargs):
        self.slug = generate_unique_slug(Blog, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog:article", kwargs={"category": self.category, "slug": self.slug})
