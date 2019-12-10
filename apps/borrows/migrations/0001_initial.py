# Generated by Django 2.1 on 2019-12-01 15:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('books', '0003_book_genre'),
        ('accounts', '0005_account_locale'),
    ]

    operations = [
        migrations.CreateModel(
            name='Borrow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('take_date', models.DateField(auto_now_add=True)),
                ('planned_return_date', models.DateField()),
                ('real_return_date', models.DateField(null=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.Book')),
                ('borrower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Account')),
            ],
        ),
    ]