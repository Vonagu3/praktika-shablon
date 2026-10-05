"""Проверка практики в парах (миссии из README.md).

Запуск из папки репозитория пары:
    python проверить.py                 # все шаги по порядку
    python проверить.py --ключ ABC123   # если на этом компьютере ключ ещё не запоминали

Скрипт ничего не меняет в репозитории, только смотрит, что уже слито в main на GitHub.
Если задан личный ключ, итог (номера выполненных шагов и подсказка) уходит руководителю — без имени и без файлов.
"""

import json
import subprocess
import sys
import urllib.request
from pathlib import Path

# В консоли Windows печатаем по-русски без ошибок кодировки.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

ПАПКА = Path(__file__).resolve().parent
MAIN = "origin/main"
ЗАГЛУШКА = "(впишите)"
# Собраны из частей, чтобы замена имён во всех файлах (миссия 0, Replace All) не задела сам скрипт.
УЧАСТНИК_1 = "Участ" + "ник 1"
УЧАСТНИК_2 = "Участ" + "ник 2"

# Куда отправлять итог: тот же сервер, что у тренажёра (www.irtuganov.pro/git-2107/).
СЕРВЕР = "https://hpmidxaovjlcjlitqjvl.supabase.co/rest/v1/rpc/git_submit"
ПУБЛИЧНЫЙ_КЛЮЧ = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhwbWlkeGFvdmpsY2psaXRxanZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkzMTI3OTYsImV4cCI6MjEwNDg4ODc5Nn0.UKlF5r7JHroaNgS8wXbRkjNPjGJ2hKufxyR-tlKAWmI"


class НеПройдено(Exception):
    pass


def git(*args, check=True):
    """Запустить git и вернуть вывод без пробелов по краям."""
    try:
        r = subprocess.run(
            ["git", "-c", "core.quotepath=false", *args],
            cwd=ПАПКА, capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except FileNotFoundError:
        raise НеПройдено("Git не установлен или терминал его не видит. Установите Git и перезапустите VS Code.")
    if check and r.returncode != 0:
        raise НеПройдено("Команда git " + " ".join(args) + " не сработала:\n      " + r.stderr.strip())
    return r.stdout.strip()


def почта():
    return git("config", "--global", "--get", "user.email", check=False)


def файл_в_main(путь):
    return git("show", f"{MAIN}:{путь}", check=False)


def ствол():
    """Коммиты, сделанные прямо в main (первые родители): сюда попадают слияния PR и миссия 0."""
    return set(git("rev-list", "--first-parent", MAIN).splitlines())


def мои_через_pr(путь):
    """Ваши коммиты с файлом, которые попали в main через ветку и pull request."""
    мои = git("log", MAIN, "--no-merges", f"--author={почта()}", "--format=%H", "--", путь, check=False).splitlines()
    прямые = ствол()
    return [c for c in мои if c not in прямые]


def слитых_pr():
    return len([s for s in git("log", MAIN, "--first-parent", "--merges", "--format=%s").splitlines()
                if s.startswith("Merge pull request")])


def проверить_файл_слит(путь, ветка):
    if мои_через_pr(путь):
        return
    if git("log", "--all", "--no-merges", f"--author={почта()}", "--format=%h", "--", путь, check=False):
        raise НеПройдено(
            f"Ваш коммит с {путь} есть, но ещё не в main на GitHub. Отправьте ветку (git push), "
            "откройте pull request, после Approve напарника нажмите Merge.")
    raise НеПройдено(
        f"Вашего изменения в {путь} нет. git checkout main, git pull, git checkout -b {ветка}, "
        "заполните свой раздел, затем add, commit, push и pull request.")


# ---------- шаги ----------

def шаг_1():
    """Миссия 0: репозиторий пары скачан, имена вписаны"""
    if not почта():
        raise НеПройдено('Не задана почта. git config --global user.email "почта, как на GitHub"')
    if git("rev-parse", "--is-inside-work-tree", check=False) != "true":
        raise НеПройдено("Эта папка не репозиторий. Скачайте его: git clone <ссылка>")
    origin = git("remote", "get-url", "origin", check=False)
    if not origin:
        raise НеПройдено("Нет связи с GitHub (origin). Репозиторий нужно получить через git clone, а не скачать архивом.")
    if "praktika-shablon" in origin:
        raise НеПройдено("Это сам шаблон. Нужен репозиторий пары: Use this template → praktika-N, потом git clone.")
    git("fetch", "origin")
    визитка = файл_в_main("визитка.md")
    if not визитка:
        raise НеПройдено("В main на GitHub нет файла визитка.md — это точно репозиторий пары?")
    if УЧАСТНИК_1 in визитка or УЧАСТНИК_2 in визитка:
        raise НеПройдено(f"Имена ещё не вписаны. Владелец: Ctrl/Cmd+Shift+H, заменить «{УЧАСТНИК_1}» и «{УЧАСТНИК_2}», затем add, commit, push.")
    return origin.removesuffix(".git").rsplit("/", 1)[-1]


def шаг_2():
    """Миссия 1: ваша визитка слита через pull request"""
    проверить_файл_слит("визитка.md", "визитка-имя")


def шаг_3():
    """Миссия 2: оба ваших PR с неделей слиты"""
    n = len(мои_через_pr("неделя.csv"))
    if n == 0:
        проверить_файл_слит("неделя.csv", "неделя1-имя")
    if n < 2:
        raise НеПройдено("Слит один PR с неделей, нужен второй раунд: ветка неделя2-имя, строки с 8 по 10 октября.")
    return f"ваших коммитов в неделя.csv: {n}"


def шаг_4():
    """Миссия 2: вы сами решили конфликт, таблица недели заполнена"""
    слияния = git("log", MAIN, "--merges", f"--author={почта()}", "--format=%H%x09%s").splitlines()
    свои = [h for h, s in (x.split("\t", 1) for x in слияния) if not s.startswith("Merge pull request")]
    решил = any("неделя.csv" in git("diff", "--name-only", f"{h}^1", h).splitlines() for h in свои)
    if not решил:
        raise НеПройдено(
            "Вы ещё не решали конфликт у себя. В вашем раунде первым сливает напарник, а вы: "
            "git pull origin main, собрать строки в VS Code, add, commit, push.")
    строки = [s for s in файл_в_main("неделя.csv").splitlines()[1:] if s.strip()]
    пустые = [s.split(",")[0] for s in строки if any(not x.strip() for x in s.split(",")[1:])]
    if len(строки) != 6 or пустые:
        raise НеПройдено("В main не все дни заполнены у обоих: " + (", ".join(пустые) or f"строк {len(строки)}, а нужно 6") +
                         ". Если раунд ещё идёт — доделайте его. Если оба раунда слиты, при конфликте чьи-то числа "
                         "пропали — допишите их через новую ветку и PR.")


def шаг_5():
    """Миссия 3: ваш вопрос слит через pull request"""
    проверить_файл_слит("вопросы.md", "вопросы-имя")
    n = len(мои_через_pr("вопросы.md"))
    return f"исправлений после review: {n - 1}" if n > 1 else ""


def шаг_6():
    """Миссия 4: ваша идея слита через pull request"""
    проверить_файл_слит("идея.md", "идея-имя")


def шаг_7():
    """Пара закончила: всё заполнено, 10 PR слиты"""
    пустые = [f for f in ("визитка.md", "вопросы.md", "идея.md") if ЗАГЛУШКА in файл_в_main(f)]
    if пустые:
        raise НеПройдено("В main ещё остались незаполненные места «(впишите)»: " + ", ".join(пустые) + ". Ждём напарника?")
    n = слитых_pr()
    if n < 10:
        raise НеПройдено(f"Слито pull request'ов: {n} из 10. Pull requests → Closed покажет, чего не хватает.")
    return f"слито PR: {n}. Напишите в чат группы и приложите картинку графика."


ШАГИ = [шаг_1, шаг_2, шаг_3, шаг_4, шаг_5, шаг_6, шаг_7]


def проверить(n, f):
    try:
        итог = f()
        print(f"  ✔ {n}. {f.__doc__}" + (f" — {итог}" if итог else ""))
        return True, "", итог
    except НеПройдено as e:
        print(f"  ✘ {n}. {f.__doc__}\n      {e}")
        return False, str(e), None


def личный_ключ():
    return git("config", "--global", "--get", "kurs.kljuch", check=False)


def отправить(выполнены, провал, текст, репо):
    """Отправить итог руководителю. Без ключа или без интернета — молча пропускаем."""
    ключ = личный_ключ()
    if not ключ:
        return
    данные = {"p_key": ключ, "p_kind": "check",
              "p_payload": {"t": "pair", "repo": (репо or "")[:40], "ok": выполнены, "fail": провал, "msg": текст[:300]}}
    запрос = urllib.request.Request(
        СЕРВЕР, data=json.dumps(данные).encode("utf-8"), method="POST",
        headers={"apikey": ПУБЛИЧНЫЙ_КЛЮЧ, "Authorization": "Bearer " + ПУБЛИЧНЫЙ_КЛЮЧ,
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(запрос, timeout=5) as ответ:
            принято = json.loads(ответ.read().decode("utf-8"))
        print("\n(Итог отправлен руководителю.)" if принято else
              "\n(Руководитель не узнал ключ. Проверьте: python проверить.py --ключ ВАШ_КЛЮЧ)")
    except Exception:
        print("\n(Не получилось отправить итог руководителю — нет интернета? Проверка при этом верная.)")


def запомнить_ключ(ключ):
    ключ = "".join(c for c in ключ.upper() if c.isalnum())
    if not ключ:
        print("Укажите ключ: python проверить.py --ключ ABC123")
        sys.exit(2)
    git("config", "--global", "kurs.kljuch", ключ)
    print(f"Ключ {ключ} запомнен. Теперь итог каждой проверки будет виден руководителю.")


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--ключ", "--key", "-k"):
        запомнить_ключ(sys.argv[2] if len(sys.argv) > 2 else "")
        return
    print("Проверяю практику в паре (смотрю main на GitHub):")
    выполнены, репо = [], ""
    for n, f in enumerate(ШАГИ, start=1):
        прошло, текст, итог = проверить(n, f)
        if n == 1 and прошло:
            репо = итог
        if not прошло:
            print("\nСделайте этот шаг и запустите проверку снова.")
            отправить(выполнены, n, текст, репо)
            sys.exit(1)
        выполнены.append(n)
    print("\nВся практика выполнена!")
    отправить(выполнены, 0, "", репо)
    if not личный_ключ():
        print("Совет: python проверить.py --ключ ВАШ_КЛЮЧ — и руководитель будет видеть ваш прогресс сам.")


if __name__ == "__main__":
    main()
