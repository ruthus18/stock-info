from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticker', models.CharField(max_length=6, unique=True)),
            ],
            options={
                'ordering': ('ticker',),
            },
        ),
        migrations.CreateModel(
            name='Insider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('slug', models.SlugField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='StockDay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateField()),
                ('open_price', models.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ('close_price', models.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ('high_price', models.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ('low_price', models.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ('volume', models.IntegerField()),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='stocks.Company')),
            ],
            options={
                'ordering': ('-created_date',),
            },
        ),
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_date', models.DateField()),
                ('relation', models.CharField(blank=True, max_length=32, null=True)),
                ('transaction_type', models.CharField(blank=True, max_length=128, null=True)),
                ('owner_type', models.CharField(blank=True, max_length=32, null=True)),
                ('last_price', models.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ('traded_shares', models.PositiveIntegerField()),
                ('held_shares', models.PositiveIntegerField()),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trades', to='stocks.Company')),
                ('insider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.Insider')),
            ],
            options={
                'ordering': ('-last_date',),
            },
        ),
        migrations.AlterUniqueTogether(
            name='stockday',
            unique_together={('company', 'created_date')},
        ),
    ]
