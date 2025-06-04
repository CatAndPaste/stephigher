import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from faker import Faker
from filer.models.imagemodels import Image as FilerImage

from django.contrib.auth import get_user_model
from news.models import News, NewsComment, Tag

User = get_user_model()


class Command(BaseCommand):
    help = "Fill DB with test data for news"

    def add_arguments(self, parser):
        parser.add_argument(
            '--news_count',
            type=int,
            default=20,
            help='number of news items'
        )
        parser.add_argument(
            '--comments',
            type=int,
            default=40,
            help='avg comments per news'
        )
        parser.add_argument(
            '--min_comments',
            type=int,
            default=30,
            help='min comments per news'
        )

    def handle(self, *args, **options):
        fake = Faker()

        num_news = options['news_count']
        max_comments = options['comments']
        min_comments = options['min_comments']

        all_images = list(FilerImage.objects.all())

        if not User.objects.exists():
            username = 'testuser'
            email = 'test@test.ru'
            password = '1234_test'
            author = User.objects.create_user(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"created author: {username} / {email}"))
        else:
            author = User.objects.order_by('?').first()
            self.stdout.write(self.style.WARNING(f"using existing author: {author.username}"))

        tags_pool = []
        for _ in range(10):
            name = fake.word().lower()
            tag, created = Tag.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"tag created: {name}"))
            tags_pool.append(tag)

        for i in range(num_news):
            title = fake.sentence(nb_words=6)
            slug = slugify(title)
            base_slug = slug
            count = 1
            while News.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            short_desc = fake.text(max_nb_chars=200)
            full_desc = '<p>' + '</p><p>'.join(fake.paragraphs(nb=random.randint(3, 7))) + '</p>'

            if all_images:
                image_choice = random.choice(all_images)
            else:
                image_choice = None

            news_item = News.objects.create(
                title=title,
                slug=slug,
                short_description=short_desc,
                full_description=full_desc,
                author=author,
                image=image_choice,
            )

            chosen_tags = random.sample(tags_pool, k=random.randint(1, 3))
            news_item.tags.add(*chosen_tags)
            news_item.save()

            self.stdout.write(self.style.SUCCESS(f"[{i+1}/{num_news}] created news: {news_item.title}"))

            num_comments = random.randint(min_comments, max_comments)
            for j in range(num_comments):
                commenter = User.objects.order_by('?').first()

                text = fake.paragraph(nb_sentences=3)
                created_at = fake.date_time_between(
                    start_date='-30d',
                    end_date='now',
                    tzinfo=timezone.get_current_timezone()
                )

                NewsComment.objects.create(
                    post=news_item,
                    author=commenter,
                    text=text,
                    created_at=created_at
                )

                if (j + 1) % 10 == 0:
                    self.stdout.write(f"{j+1}/{num_comments} comments added")

        self.stdout.write(self.style.SUCCESS("DB filled with news and comments"))
