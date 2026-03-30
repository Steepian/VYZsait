import sqlite3
import re
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from main.models import University, Specialty

class Command(BaseCommand):
    help = 'Импорт вузов и специальностей из monvoscrap SQLite базы'

    def add_arguments(self, parser):
        parser.add_argument(
            '--db', type=str, default='db.sqlite',
            help='Путь к файлу monvoscrap db.sqlite'
        )

    def handle(self, *args, **options):
        db_path = options['db']
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. Импорт вузов
        self.stdout.write('Импорт вузов...')
        university_map = {}

        cursor.execute('SELECT uid, name, address, ministry, owner, fdid FROM universities')
        for uid, name, address, ministry, owner, fdid in cursor.fetchall():
            # Извлечение города из адреса
            city = ''
            if address:
                # Пытаемся найти "г. Город" или "г Город"
                match = re.search(r'(?:г\.?\s*)([^,;]+)', address, re.IGNORECASE)
                if match:
                    city = match.group(1).strip()
                else:
                    # Если не нашли, берем первую часть до запятой
                    parts = address.split(',')
                    first = parts[0].strip()
                    # Если первая часть слишком длинная, вероятно, не город
                    if len(first) <= 50:
                        city = first

            # Формируем описание из доступной информации
            description_parts = []
            if address:
                description_parts.append(f"Адрес: {address}")
            if ministry:
                description_parts.append(f"Ведомство: {ministry}")
            if owner:
                description_parts.append(f"Форма собственности: {owner}")
            if not description_parts:
                description_parts.append("Вуз из базы мониторинга.")
            description = "\n".join(description_parts)

            try:
                # Используем get_or_create, чтобы избежать дубликатов по названию
                uni, created = University.objects.get_or_create(
                    name=name,
                    defaults={
                        'city': city,
                        'description': description,
                        'created_at': '2025-01-01',  # временная дата, можно будет уточнить
                        'updated_at': '2025-01-01',
                        'rating': 0.0,
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  Добавлен вуз: {name}'))
                else:
                    self.stdout.write(f'  Вуз уже существует: {name}')
                university_map[uid] = uni
            except IntegrityError as e:
                self.stderr.write(self.style.ERROR(f'Ошибка при создании вуза "{name}": {e}'))
                continue

        # 2. Импорт специальностей (УГН)
        self.stdout.write('\nИмпорт специальностей...')
        cursor.execute('SELECT ugnid, name FROM ugn')
        for ugnid, name in cursor.fetchall():
            try:
                spec, created = Specialty.objects.get_or_create(
                    code=str(ugnid),
                    name=name,
                    defaults={'description': '', 'rating': 0.0}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'  Добавлена специальность: {name} (код {ugnid})'))
                else:
                    self.stdout.write(f'  Специальность уже существует: {name}')
            except IntegrityError as e:
                self.stderr.write(self.style.ERROR(f'Ошибка при создании специальности "{name}": {e}'))

        # 3. Привязка специальностей к вузам через ManyToMany
        self.stdout.write('\nПривязка специальностей к вузам...')
        # Выбираем последний год для каждой пары (uid, ugnid)
        cursor.execute('''
            SELECT uid, ugnid, MAX(year) as last_year
            FROM uni_ugn
            GROUP BY uid, ugnid
        ''')
        results = cursor.fetchall()
        total = len(results)
        processed = 0
        for uid, ugnid, year in results:
            processed += 1
            if processed % 100 == 0:
                self.stdout.write(f'  Обработано {processed}/{total} связей')
            uni = university_map.get(uid)
            if not uni:
                self.stderr.write(f'  Вуз с uid {uid} не найден, пропускаем')
                continue
            spec = Specialty.objects.filter(code=str(ugnid)).first()
            if not spec:
                self.stderr.write(f'  Специальность с кодом {ugnid} не найдена, пропускаем')
                continue
            # Добавляем связь, если её ещё нет
            spec.universities.add(uni)
            # Не выводим каждую связь, чтобы не засорять лог
        self.stdout.write(self.style.SUCCESS(f'Обработано {processed} связей'))

        conn.close()
        self.stdout.write(self.style.SUCCESS('Импорт завершён'))