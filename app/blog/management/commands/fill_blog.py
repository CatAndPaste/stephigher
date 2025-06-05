import random
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from faker import Faker
from filer.models.imagemodels import Image as FilerImage

from django.contrib.auth import get_user_model
from blog.models import BlogPost, Comment, Tag

User = get_user_model()


class Command(BaseCommand):
    help = "Fill DB with test data for blog"

    def add_arguments(self, parser):
        parser.add_argument(
            '--posts',
            type=int,
            default=20,
            help='posts number'
        )
        parser.add_argument(
            '--comments',
            type=int,
            default=40,
            help='avg comments number'
        )
        parser.add_argument(
            '--min_comments',
            type=int,
            default=30,
            help='min comments number'
        )

    def handle(self, *args, **options):
        fake = Faker()

        num_posts = options['posts']
        max_comments = options['comments']
        min_comments = options['min_comments']

        all_filer_images = list(FilerImage.objects.all())

        if not User.objects.exists():
            username = 'testuser'
            email = 'test@test.ru'
            password = '1234_test'
            user = User.objects.create_user(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"author: {username} / {email}"))
        else:
            user = User.objects.order_by('?').first()
            self.stdout.write(self.style.WARNING(f"existed author: {user.username}"))

        tags_pool = []
        for _ in range(10):
            name = fake.word().lower()
            tag, created = Tag.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"tag created: {name}"))
            tags_pool.append(tag)

        for i in range(num_posts):
            title = fake.sentence(nb_words=6)
            slug = slugify(title)
            original_slug = slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1

            short_desc = fake.text(max_nb_chars=200)
            full_desc = '<p>' + '</p><p>'.join(fake.paragraphs(nb=random.randint(3, 7))) + '</p>'

            if all_filer_images:
                image_choice = random.choice(all_filer_images)
            else:
                image_choice = None

            post = BlogPost.objects.create(
                title=title,
                slug=slug,
                short_description=short_desc,
                full_description=full_desc,
                author=user,
                image=image_choice,
            )

            chosen_tags = random.sample(tags_pool, k=random.randint(1, 3))
            post.tags.add(*chosen_tags)
            post.save()

            self.stdout.write(self.style.SUCCESS(f"[{i+1}/{num_posts}] created post: {post.title}"))

            num_comments = random.randint(min_comments, max_comments)
            for j in range(num_comments):
                author = User.objects.order_by('?').first()

                comment_text = fake.paragraph(nb_sentences=3)
                created_at = fake.date_time_between(start_date='-30d', end_date='now',
                                                    tzinfo=timezone.get_current_timezone())

                Comment.objects.create(
                    post=post,
                    author=author,
                    text=comment_text,
                    created_at=created_at
                )

                if (j + 1) % 10 == 0:
                    self.stdout.write(f"{j+1}/{num_comments} comments added")

        self.stdout.write(self.style.SUCCESS("DB filled >:D"))