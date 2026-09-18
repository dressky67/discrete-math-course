import os
import sys
import glob
import shutil
import typst

from preamble import PREAMBLE
from convert_to_typst import convert_markdown_to_typst

sys.stdout.reconfigure(encoding='utf-8')

BOOK_COVER_AND_FRONTMATTER = '''
#set page(
  paper: "a4",
  margin: (x: 2.5cm, top: 3cm, bottom: 2.5cm),
  header: none,
  footer: none
)

#align(center + horizon)[
  #block(
    stroke: 2pt + rgb("#0284c7"),
    inset: 24pt,
    radius: 8pt,
    fill: rgb("#f8fafc"),
    width: 100%
  )[
    #v(1em)
    #text(size: 14pt, weight: "bold", fill: rgb("#0369a1"))[ОТКРЫТЫЙ УЧЕБНО-МЕТОДИЧЕСКИЙ КОМПЛЕКС]
    
    #v(1.5em)
    #text(size: 26pt, weight: "bold", fill: rgb("#0f172a"))[ДИСКРЕТНАЯ МАТЕМАТИКА\\ И ОСНОВЫ ТЕОРИИ МАТРИЦ]
    
    #v(1em)
    #text(size: 14pt, style: "italic", fill: rgb("#334155"))[Полный академический курс для самостоятельного изучения с нуля\\ до олимпиадного и прикладного инженерного уровня]
    
    #v(2em)
    #line(length: 60%, stroke: 1pt + rgb("#cbd5e1"))
    #v(1.5em)
    
    #text(size: 11pt, fill: rgb("#475569"))[
      *9 фундаментальных глав • 90+ детально разобранных задач • Строгие доказательства*\\
      *Интерактивные веб-лаборатории на GitHub Pages*\\
      #link("https://dressky67.github.io/discrete-math-course/")
    ]
    
    #v(2.5em)
    #text(size: 10pt, fill: rgb("#64748b"))[2026 г.]
  ]
]

#pagebreak()

#set page(
  paper: "a4",
  margin: (x: 2cm, top: 2.5cm, bottom: 2.5cm),
  header: align(right)[_Дискретная математика и основы теории матриц_],
  footer: align(center)[#context counter(page).display()]
)
#counter(page).update(1)

= Предисловие: Как изучать этот курс

Настоящий учебник представляет собой единый систематический курс дискретной математики и основ матричной алгебры, созданный для углубленного самостоятельного освоения. Курс спроектирован по принципу *«от фундаментальных абстракций — к вычислительным методам и реальным приложениям»*.

== Методическая структура каждой главы

Каждая глава книги построена по строгому дидактическому канону:
1. *Мотивация и интуиция*: связь изучаемых понятий с задачами программирования, алгоритмов и физического моделирования.
2. *Формальная теория*: строгие определения, формулировки лемм и теорем, аналитические доказательства ключевых результатов.
3. *Разобранные примеры*: не менее двух типовых примеров с пошаговыми вычислениями и комментариями на каждый ключевой концепт.
4. *Практикум и банк задач*: от 8 до 10 задач, упорядоченных по возрастанию сложности (базовые, повышенной сложности и исследовательско-олимпиадные) с полными решениями.
5. *Интерактивные лаборатории*: ссылки на интерактивные визуализаторы, доступные в браузере на платформе GitHub Pages:
   #align(center)[#link("https://dressky67.github.io/discrete-math-course/")]
6. *Рекомендуемая литература*: список авторитетных монографий и классических учебников (Кнут, Виленкин, Новиков, Грэхем, Стрэнг, Кормен).

== Об авторах и проекте

Курс разработан в рамках открытой образовательной инициативы. Исходные коды всех интерактивных моделей и полные исходные тексты курса размещены в репозитории GitHub:
#align(center)[#link("https://github.com/dressky67/discrete-math-course")]

#v(1em)
#line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
#v(1em)

= Содержание

#outline(indent: auto, depth: 2, title: none)

#pagebreak()
'''

def build_pdf():
    print("=== STARTING UNIFIED PDF BUILD ===")
    
    chapters = sorted(glob.glob("content/ch*.md"))
    print(f"Found {len(chapters)} chapters to compile.")
    
    full_typst = PREAMBLE + "\n" + BOOK_COVER_AND_FRONTMATTER + "\n"
    
    for i, ch_path in enumerate(chapters, 1):
        ch_name = os.path.basename(ch_path)
        print(f"Processing Chapter {i}: {ch_name}...")
        with open(ch_path, "r", encoding="utf-8") as f:
            md = f.read()
            
        typ_chapter = convert_markdown_to_typst(md)
        full_typst += f"\n// CHAPTER {i}\n" + typ_chapter + "\n#pagebreak()\n"
        
    typ_source_path = "build/book.typ"
    pdf_output_path = "build/discrete_math_course.pdf"
    root_pdf_path = "discrete_math_course.pdf"
    
    print(f"Writing complete Typst source to {typ_source_path}...")
    with open(typ_source_path, "w", encoding="utf-8") as f:
        f.write(full_typst)
        
    source_size = os.path.getsize(typ_source_path)
    print(f"Typst source size: {source_size:,} bytes.")
    
    print("Compiling Typst source into unified publication-quality PDF...")
    try:
        typst.compile(typ_source_path, output=pdf_output_path)
        pdf_size = os.path.getsize(pdf_output_path)
        print(f"\nSUCCESS! Generated {pdf_output_path} ({pdf_size:,} bytes).")
        
        # Copy to root directory for GitHub Pages direct download
        shutil.copyfile(pdf_output_path, root_pdf_path)
        print(f"Copied to root: {root_pdf_path} ({os.path.getsize(root_pdf_path):,} bytes).")
        return True
    except Exception as e:
        print(f"\nCOMPILATION FAILED: {e}")
        if hasattr(e, 'diagnostic') and e.diagnostic:
            print("\nDiagnostic:\n", e.diagnostic)
        return False

if __name__ == "__main__":
    success = build_pdf()
    sys.exit(0 if success else 1)
