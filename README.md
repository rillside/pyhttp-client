<div align="center">

<img src="assets/avatar.png" width="120" alt="HTTP Client"/>

# HTTP Client

Простой и аккуратный GUI-клиент для отправки HTTP-запросов.
На Python + [customtkinter](https://github.com/TomSchimansky/CustomTkinter) + [requests](https://requests.readthedocs.io/).

</div>

---

## Возможности

- **Методы:** GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS.
- **Адрес (URL):** если не указать схему, автоматически подставляется `http://`. Enter в поле адреса сразу отправляет запрос.
- **Заголовки:** построчно `Ключ: Значение` или целиком JSON-объектом. Строки, начинающиеся с `#`, игнорируются.
- **Тело запроса:** произвольный текст или JSON.
- **Ответ:** статус, время ответа (мс), размер, заголовки и тело. JSON автоматически форматируется с отступами.
- Запрос выполняется **в отдельном потоке** — интерфейс не зависает во время ожидания.
- Тёмная тема, иконка окна и значок в панели задач Windows.

---

## Установка готовой сборки (Windows)

1. Откройте вкладку [**Releases**](../../releases) и скачайте `HttpClient-windows.zip`.
2. Распакуйте архив в любую папку.
3. Запустите `HttpClient.exe` из распакованной папки.

> Приложение не требует установленного Python.

### ⚠️ Предупреждение антивируса / SmartScreen

Сборка распространяется **без сертификата подписи кода (Code Signing)**, поэтому
Windows SmartScreen или антивирус могут показать предупреждение о «неизвестном
издателе». Это **ложное срабатывание**, характерное для любых неподписанных
приложений на Python/PyInstaller.

Сборка сделана в режиме `--onedir` (папка вместо самораспаковывающегося exe),
без UPX — это заметно снижает число срабатываний. Полностью убрать
предупреждение можно только покупкой сертификата Authenticode.

Если SmartScreen всё же сработал: **«Подробнее» → «Выполнить в любом случае»**.

---

## Запуск из исходников

```bash
pip install -r requirements.txt
python http_client.py
```

Требуется Python 3.10+.

---

## Самостоятельная сборка exe

```bash
pip install -r requirements.txt
pyinstaller --noconfirm HttpClient.spec
```

Результат — папка `dist/HttpClient/` с `HttpClient.exe` внутри.
Параметры сборки описаны в [`HttpClient.spec`](HttpClient.spec).

## Автосборка на GitHub (CI/CD)

Сборка exe полностью автоматизирована через GitHub Actions —
см. [`.github/workflows/build.yml`](.github/workflows/build.yml).

- **Релиз с exe** создаётся автоматически при пуше тега вида `vX.Y.Z`:

  ```bash
  git tag v1.0.0
  git push origin v1.0.0
  ```

  Workflow соберёт exe на `windows-latest`, упакует в zip и приложит к новому
  GitHub Release (с автоматическими release notes).

- **Ручной прогон** доступен на вкладке **Actions → Build Windows EXE →
  Run workflow** — собранный zip будет доступен как artifact (без создания
  релиза).

> Бинарники намеренно **не** коммитятся в репозиторий (`dist/`, `build/` в
> `.gitignore`) — их собирает и публикует CI.

---

## Структура проекта

```
http_client/
├── http_client.py          # приложение (GUI + логика запросов)
├── HttpClient.spec         # конфигурация сборки PyInstaller (onedir)
├── requirements.txt        # зависимости
├── assets/
│   ├── icon.ico            # иконка приложения
│   └── avatar.png          # аватар репозитория
└── .github/workflows/
    └── build.yml           # CI: сборка exe и публикация релиза
```

---

## Лицензия

[MIT](LICENSE)
