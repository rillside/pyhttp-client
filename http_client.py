"""
Простой HTTP-клиент с графическим интерфейсом на customtkinter.

Возможности:
    - выбор типа запроса (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS);
    - ввод адреса (URL);
    - заголовки (по строкам "Ключ: Значение" или JSON-объектом);
    - тело запроса (произвольный текст / JSON);
    - вывод статуса, времени ответа, заголовков и тела ответа.

Запрос выполняется в отдельном потоке, поэтому интерфейс не зависает.
"""

import json
import os
import sys
import threading
import time

import customtkinter as ctk
import requests

METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]

APP_ID = "rillside.httpclient.1"


def resource_path(relative):
    """Путь к ресурсу: работает и из исходников, и из собранного exe."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class HttpClientApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("HTTP Client")
        self.geometry("900x700")
        self.minsize(700, 550)
        self._set_window_icon()

        # сетка: расширяется средняя зона с табами и зона ответа
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(4, weight=2)

        self._build_url_row()
        self._build_request_tabs()
        self._build_send_row()
        self._build_response_area()

    def _set_window_icon(self):
        ico = resource_path(os.path.join("assets", "icon.ico"))
        if os.path.exists(ico):
            try:
                self.iconbitmap(ico)
            except Exception:  # noqa: BLE001 — иконка не критична для работы
                pass

    # ------------------------------------------------------------------ UI ---
    def _build_url_row(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=0, column=0, padx=12, pady=(12, 6), sticky="ew")
        frame.grid_columnconfigure(1, weight=1)

        self.method_menu = ctk.CTkOptionMenu(frame, values=METHODS, width=110)
        self.method_menu.set("GET")
        self.method_menu.grid(row=0, column=0, padx=(8, 6), pady=8)

        self.url_entry = ctk.CTkEntry(
            frame, placeholder_text="https://api.example.com/endpoint"
        )
        self.url_entry.grid(row=0, column=1, padx=6, pady=8, sticky="ew")
        self.url_entry.bind("<Return>", lambda _e: self.send_request())

    def _build_request_tabs(self):
        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=2, column=0, padx=12, pady=6, sticky="nsew")

        body_tab = self.tabs.add("Тело запроса")
        headers_tab = self.tabs.add("Заголовки")

        body_tab.grid_columnconfigure(0, weight=1)
        body_tab.grid_rowconfigure(0, weight=1)
        headers_tab.grid_columnconfigure(0, weight=1)
        headers_tab.grid_rowconfigure(0, weight=1)

        self.body_text = ctk.CTkTextbox(body_tab, wrap="none")
        self.body_text.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        self.headers_text = ctk.CTkTextbox(headers_tab, wrap="none")
        self.headers_text.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.headers_text.insert(
            "1.0",
            "# По одной на строку: Ключ: Значение\n"
            "# Или JSON-объект целиком\n"
            "Content-Type: application/json",
        )

    def _build_send_row(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=3, column=0, padx=12, pady=4, sticky="ew")
        frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(frame, text="Готово", anchor="w")
        self.status_label.grid(row=0, column=0, sticky="ew", padx=4)

        self.send_button = ctk.CTkButton(
            frame, text="Отправить", width=140, command=self.send_request
        )
        self.send_button.grid(row=0, column=1, padx=4)

    def _build_response_area(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=4, column=0, padx=12, pady=(6, 12), sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Ответ", anchor="w").grid(
            row=0, column=0, sticky="ew", padx=8, pady=(6, 0)
        )

        self.response_text = ctk.CTkTextbox(frame, wrap="none")
        self.response_text.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)

    # ------------------------------------------------------------- логика ---
    def _parse_headers(self):
        """Преобразует текст заголовков в словарь."""
        raw = self.headers_text.get("1.0", "end").strip()
        if not raw:
            return {}

        # пробуем как JSON
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
        except json.JSONDecodeError:
            pass

        # построчный разбор "Ключ: Значение"
        headers = {}
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()
        return headers

    def send_request(self):
        url = self.url_entry.get().strip()
        if not url:
            self._set_status("Укажите адрес запроса", error=True)
            return

        if not url.lower().startswith(("http://", "https://")):
            url = "http://" + url

        method = self.method_menu.get()

        try:
            headers = self._parse_headers()
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Ошибка в заголовках: {exc}", error=True)
            return

        body = self.body_text.get("1.0", "end").strip()

        self.send_button.configure(state="disabled")
        self._set_status("Отправка запроса...")

        thread = threading.Thread(
            target=self._do_request,
            args=(method, url, headers, body),
            daemon=True,
        )
        thread.start()

    def _do_request(self, method, url, headers, body):
        data = body.encode("utf-8") if body else None
        try:
            start = time.perf_counter()
            response = requests.request(
                method,
                url,
                headers=headers,
                data=data,
                timeout=30,
            )
            elapsed = (time.perf_counter() - start) * 1000
            self.after(0, self._show_response, response, elapsed)
        except requests.RequestException as exc:
            self.after(0, self._show_error, exc)

    def _show_response(self, response, elapsed_ms):
        lines = [
            f"{response.status_code} {response.reason}   "
            f"({elapsed_ms:.0f} мс, {len(response.content)} байт)",
            "",
            "--- Заголовки ответа ---",
        ]
        for key, value in response.headers.items():
            lines.append(f"{key}: {value}")

        lines.append("")
        lines.append("--- Тело ответа ---")

        # красиво печатаем JSON, если это он
        text = response.text
        ctype = response.headers.get("Content-Type", "")
        if "application/json" in ctype.lower():
            try:
                parsed = json.loads(text)
                text = json.dumps(parsed, ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                pass
        lines.append(text)

        self._set_response("\n".join(lines))
        ok = 200 <= response.status_code < 400
        self._set_status(
            f"{response.status_code} {response.reason} — {elapsed_ms:.0f} мс",
            error=not ok,
        )
        self.send_button.configure(state="normal")

    def _show_error(self, exc):
        self._set_response(f"Ошибка запроса:\n\n{exc}")
        self._set_status(f"Ошибка: {exc}", error=True)
        self.send_button.configure(state="normal")

    # ----------------------------------------------------------- хелперы ---
    def _set_response(self, text):
        self.response_text.delete("1.0", "end")
        self.response_text.insert("1.0", text)

    def _set_status(self, text, error=False):
        self.status_label.configure(
            text=text,
            text_color="#ff6b6b" if error else ("gray80", "gray20"),
        )


def _set_app_user_model_id():
    """Чтобы Windows показывал нашу иконку в панели задач"""
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    except Exception:  # noqa: BLE001
        pass


def main():
    _set_app_user_model_id()
    app = HttpClientApp()
    app.mainloop()


if __name__ == "__main__":
    main()
