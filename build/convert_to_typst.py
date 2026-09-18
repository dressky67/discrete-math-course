import re
import os
import glob

# Master mapping of LaTeX command to Typst equivalent
LATEX_SYMBOLS = {
    # Logic & Relations
    'longleftrightarrow': ' <=> ',
    'leftrightarrow': ' <=> ',
    'longrightarrow': ' --> ',
    'impliedby': ' <= ',
    'implies': ' => ',
    'iff': ' <=> ',
    'to': ' -> ',
    'leftarrow': ' <- ',
    'rightarrow': ' -> ',
    'land': ' and ',
    'lor': ' or ',
    'neg': ' not ',
    'not': ' not ',
    'top': ' top ',
    'bot': ' bot ',
    'equiv': ' equiv ',
    'neq': ' != ',
    'le': ' <= ',
    'leq': ' <= ',
    'ge': ' >= ',
    'geq': ' >= ',
    'sim': ' tilde ',
    'tilde': ' tilde ',
    'approx': ' approx ',
    'll': ' << ',
    'prec': ' prec ',
    'mid': ' | ',
    'nmid': ' cancel(|) ',
    
    # Sets
    'cap': ' inter ',
    'cup': ' union ',
    'bigcap': ' inter.big ',
    'bigcup': ' union.big ',
    'bigwedge': ' and.big ',
    'bigvee': ' or.big ',
    'subset': ' subset ',
    'subseteq': ' subset.eq ',
    'subsetneq': ' subset.neq ',
    'in': ' in ',
    'notin': ' not in ',
    'setminus': ' without ',
    'emptyset': ' emptyset ',
    
    # Quantifiers & Special
    'forall': ' forall ',
    'exists': ' exists ',
    'infty': ' oo ',
    'blacksquare': ' qed ',
    'triangle': ' triangle ',
    'downarrow': ' arrow.b ',
    
    # Operations
    'cdot': ' dot ',
    'times': ' times ',
    'oplus': ' ⊕ ',
    'odot': ' ⊙ ',
    'circ': ' compose ',
    'pm': ' plus.minus ',
    'perp': ' perp ',
    
    # Functions
    'det': ' det ',
    'gcd': ' gcd ',
    'deg': ' deg ',
    'dim': ' dim ',
    'sin': ' sin ',
    'cos': ' cos ',
    'ln': ' ln ',
    'log': ' log ',
    'min': ' min ',
    'max': ' max ',
    'inf': ' inf ',
    'sup': ' sup ',
    'sum': ' sum ',
    'prod': ' product ',
    'lim': ' lim ',
    
    # Dots
    'ddots': ' dots.down ',
    'vdots': ' dots.v ',
    'cdots': ' dots ',
    'ldots': ' dots ',
    'dots': ' dots ',
    
    # Greek
    'alpha': ' alpha ',
    'beta': ' beta ',
    'gamma': ' gamma ',
    'delta': ' delta ',
    'epsilon': ' epsilon ',
    'varepsilon': ' epsilon.alt ',
    'zeta': ' zeta ',
    'eta': ' eta ',
    'theta': ' theta ',
    'iota': ' iota ',
    'kappa': ' kappa ',
    'lambda': ' lambda ',
    'mu': ' mu ',
    'nu': ' nu ',
    'xi': ' xi ',
    'pi': ' pi ',
    'rho': ' rho ',
    'sigma': ' sigma ',
    'tau': ' tau ',
    'phi': ' phi ',
    'varphi': ' phi.alt ',
    'chi': ' chi ',
    'psi': ' psi ',
    'omega': ' omega ',
    'Delta': ' Delta ',
    'Gamma': ' Gamma ',
    'Theta': ' Theta ',
    'Lambda': ' Lambda ',
    'Sigma': ' Sigma ',
    'Phi': ' Phi ',
    'Psi': ' Psi ',
    'Omega': ' Omega ',
    
    # Brackets & Angles
    'langle': ' chevron.l ',
    'rangle': ' chevron.r ',
    'lceil': ' ceil.l ',
    'rceil': ' ceil.r ',
    'lfloor': ' floor.l ',
    'rfloor': ' floor.r ',
    
    # Spacing
    'qquad': '   ',
    'quad': ' ',
}

SORTED_COMMANDS = sorted(LATEX_SYMBOLS.keys(), key=lambda c: len(c), reverse=True)

def replace_balanced_frac(text):
    # Replaces \frac{num}{den} handling arbitrary nested braces
    while r'\frac{' in text:
        idx = text.find(r'\frac{')
        if idx == -1:
            break
        # find matching closing brace for numerator
        depth = 0
        num_start = idx + 6
        num_end = -1
        for i in range(num_start - 1, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    num_end = i
                    break
        if num_end == -1 or num_end + 1 >= len(text) or text[num_end + 1] != '{':
            # Malformed frac, break to avoid infinite loop
            text = text[:idx] + "frac" + text[idx+5:]
            continue
        # find matching closing brace for denominator
        depth = 0
        den_start = num_end + 2
        den_end = -1
        for i in range(den_start - 1, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    den_end = i
                    break
        if den_end == -1:
            text = text[:idx] + "frac" + text[idx+5:]
            continue
        num = text[num_start:num_end]
        den = text[den_start:den_end]
        text = text[:idx] + f"(({num}) / ({den}))" + text[den_end + 1:]
    return text

def replace_underbrace(text):
    while r'\underbrace{' in text:
        idx = text.find(r'\underbrace{')
        depth = 0
        body_start = idx + 12
        body_end = -1
        for i in range(body_start - 1, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    body_end = i
                    break
        if body_end == -1:
            break
        body = text[body_start:body_end]
        rem = text[body_end+1:]
        label = ""
        consumed = body_end + 1
        m_lbl = re.match(r'^\s*_\s*\{([^{}]+)\}', rem)
        if m_lbl:
            label = m_lbl.group(1)
            consumed = body_end + 1 + m_lbl.end()
        elif rem.startswith('_('):
            m_lbl2 = re.match(r'^\s*_\s*\(([^()]+)\)', rem)
            if m_lbl2:
                label = m_lbl2.group(1)
                consumed = body_end + 1 + m_lbl2.end()
        elif rem.startswith('_'):
            m_lbl3 = re.match(r'^\s*_\s*([a-zA-Z0-9])', rem)
            if m_lbl3:
                label = m_lbl3.group(1)
                consumed = body_end + 1 + m_lbl3.end()
        
        if label:
            text = text[:idx] + f" underbrace({body}, {label}) " + text[consumed:]
        else:
            text = text[:idx] + f" underbrace({body}) " + text[consumed:]
    return text

def convert_latex_math(math_str):
    s = math_str
    
    # Environments: pmatrix, bmatrix, vmatrix, array
    def replace_matrix(m):
        env = m.group(1)
        content = m.group(2).strip()
        rows = content.split(r'\\')
        delim = ""
        if env == "bmatrix":
            delim = 'delim: "[", '
        elif env == "vmatrix":
            delim = 'delim: "|", '
        
        row_strs = []
        for r in rows:
            r = r.strip()
            if not r:
                continue
            cols = [c.strip() for c in r.split('&')]
            row_strs.append(", ".join(cols))
        return f"mat({delim}{'; '.join(row_strs)})"

    s = re.sub(r'\\begin\{(pmatrix|bmatrix|vmatrix|array)\}(?:\{[^}]*\})?(.*?)\\end\{\1\}', replace_matrix, s, flags=re.DOTALL)
    s = re.sub(r'\\begin\{aligned\}(.*?)\\end\{aligned\}', r'\1', s, flags=re.DOTALL)
    
    # Cases environment
    def replace_cases(m):
        content = m.group(1).strip()
        rows = content.split(r'\\')
        row_strs = []
        for r in rows:
            r = r.strip()
            if not r:
                continue
            r_clean = r.replace('&', ' ')
            row_strs.append(r_clean)
        return f"cases({', '.join(row_strs)})"

    s = re.sub(r'\\begin\{cases\}(.*?)\\end\{cases\}', replace_cases, s, flags=re.DOTALL)
    
    # Early macros
    s = re.sub(r'\\phantom\{([^{}]+)\}', r' ', s)
    s = re.sub(r'\\overline\{\s*\}', 'overline(dot)', s)
    s = re.sub(r'\\bar\{\s*\}', 'overline(dot)', s)
    for _ in range(3):
        s = re.sub(r'\\overline\{([^{}]+)\}', r'overline(\1)', s)
        s = re.sub(r'\\bar\{([^{}]+)\}', r'overline(\1)', s)

    # Fractions via brace counting
    s = replace_balanced_frac(s)

    for _ in range(5):
        s = re.sub(r'\\sqrt\{([^{}]+)\}', r' sqrt(\1)', s)
        s = re.sub(r'\\binom\{([^{}]+)\}\{([^{}]+)\}', r'binom(\1, \2)', s)
        
    s = replace_underbrace(s)
    s = re.sub(r'\\xrightarrow\{([^{}]+)\}', r'-->', s)
    
    # Text & Operators: op("...") instead of math.op("...")
    s = re.sub(r'\\text\{([^{}]+)\}', r'"\1"', s)
    s = re.sub(r'\\operatorname\{([^{}]+)\}', r'op("\1")', s)
    s = re.sub(r'\\mathbf\{([^{}]+)\}', r'bold(\1)', s)
    s = re.sub(r'\\mathbb\{([^{}]+)\}', r'bb(\1)', s)
    s = re.sub(r'\\mathcal\{([^{}]+)\}', r'cal(\1)', s)
    s = re.sub(r'\\pmod\{([^{}]+)\}', r'(mod \1)', s)
    s = re.sub(r'\\pmod\s+([a-zA-Z0-9]+)', r'(mod \1)', s)
    s = re.sub(r'\\bmod(?![a-zA-Z])', 'mod', s)
    
    # Delimiters
    s = re.sub(r'\\left\.', '', s)
    s = re.sub(r'\\right\.', '', s)
    s = re.sub(r'\\left\(', '(', s)
    s = re.sub(r'\\right\)', ')', s)
    s = re.sub(r'\\left\[', '[', s)
    s = re.sub(r'\\right\]', ']', s)
    s = re.sub(r'\\left\\\{', '{', s)
    s = re.sub(r'\\right\\\}', '}', s)
    s = re.sub(r'\\left\|', '|', s)
    s = re.sub(r'\\right\|', '|', s)
    s = re.sub(r'\\left(?![a-zA-Z])', '', s)
    s = re.sub(r'\\right(?![a-zA-Z])', '', s)

    # Commands replacement
    for cmd in SORTED_COMMANDS:
        rep = LATEX_SYMBOLS[cmd]
        s = re.sub(r'\\' + cmd + r'(?![a-zA-Z])', rep, s)
        
    s = re.sub(r'\\,', ' ', s)
    s = re.sub(r'\\;', ' ', s)
    s = re.sub(r'\\!', '', s)
    
    # Smart subscripts
    def fix_subscript(m):
        inner = m.group(1).strip()
        if len(inner) in (2, 3) and inner.isalnum():
            return f'_({", ".join(list(inner))})'
        return f'_({inner})'

    s = re.sub(r'_\{([^{}]+)\}', fix_subscript, s)
    s = re.sub(r'\^\{([^{}]+)\}', r'^(\1)', s)
    s = re.sub(r'\\\{', '{', s)
    s = re.sub(r'\\\}', '}', s)
    
    return s

def convert_markdown_to_typst(md_content):
    md_content = md_content.lstrip('\ufeff')
    
    disp_maths = []
    def save_disp_math(m):
        converted = convert_latex_math(m.group(1).strip())
        disp_maths.append(converted)
        return f"\n\n___DISP_MATH_{len(disp_maths)-1}___\n\n"
    
    md_content = re.sub(r'\$\$(.*?)\$\$', save_disp_math, md_content, flags=re.DOTALL)
    
    lines = md_content.split('\n')
    out_lines = []
    
    in_code_block = False
    in_quote_block = False
    quote_buffer = []
    
    in_table = False
    table_rows = []
    
    def flush_quote():
        nonlocal in_quote_block, quote_buffer
        if quote_buffer:
            content = " ".join(quote_buffer)
            border_color = 'rgb("#38bdf8")'
            bg_color = 'rgb("#f0f9ff")'
            if "Определение" in content:
                border_color = 'rgb("#0284c7")'
                bg_color = 'rgb("#f0f9ff")'
            elif "Теорема" in content:
                border_color = 'rgb("#7c3aed")'
                bg_color = 'rgb("#f5f3ff")'
            elif "Пример" in content:
                border_color = 'rgb("#059669")'
                bg_color = 'rgb("#ecfdf5")'
            elif "Задача" in content:
                border_color = 'rgb("#d97706")'
                bg_color = 'rgb("#fffbeb")'
            
            formatted = format_inline(content)
            out_lines.append(f'#rect(width: 100%, stroke: (left: 3.5pt + {border_color}), fill: {bg_color}, inset: 10pt, radius: (right: 4pt))[#par(justify: true)[{formatted}]]\n')
            quote_buffer = []
        in_quote_block = False

    def flush_table():
        nonlocal in_table, table_rows
        if table_rows:
            headers = table_rows[0]
            num_cols = len(headers)
            col_spec = ", ".join(["1fr"] * num_cols)
            out_lines.append(f'#v(0.5em)\n#align(center)[#table(')
            out_lines.append(f'  columns: ({col_spec}),')
            out_lines.append('  fill: (x, y) => if y == 0 { rgb("#f1f5f9") } else if calc.even(y) { rgb("#f8fafc") } else { none },')
            out_lines.append('  stroke: 0.5pt + rgb("#cbd5e1"),')
            
            for h in headers:
                out_lines.append(f'  [* {format_inline(h.strip())} *],')
            for row in table_rows[1:]:
                row_cells = row + [''] * (num_cols - len(row))
                for c in row_cells[:num_cols]:
                    out_lines.append(f'  [{format_inline(c.strip())}],')
            out_lines.append(')]\n#v(0.5em)\n')
            table_rows = []
        in_table = False

    def format_inline(text):
        codes = []
        def code_save(m):
            codes.append(m.group(1))
            return f'___CODE_{len(codes)-1}___'
        t = re.sub(r'`([^`]+)`', code_save, text)
        
        def inl_math(m):
            m_body = convert_latex_math(m.group(1).strip())
            return f'${m_body}$'
        t = re.sub(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', inl_math, t)
        
        t = re.sub(r'\[(.*?)\]\((.*?)\)', r'#link("\2")[\1]', t)
        t = re.sub(r'\*\*(.*?)\*\*', r'*\1*', t)
        t = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'_\1_', t)
        
        for i, code in enumerate(codes):
            t = t.replace(f'___CODE_{i}___', f'`{code}`')
            
        return t

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        m_dm = re.match(r'^___DISP_MATH_(\d+)___$', stripped)
        if m_dm:
            if in_quote_block:
                flush_quote()
            if in_table:
                flush_table()
            idx = int(m_dm.group(1))
            out_lines.append(f'\n$ {disp_maths[idx]} $\n')
            i += 1
            continue

        if stripped.startswith('```'):
            if in_quote_block:
                flush_quote()
            if in_table:
                flush_table()
            in_code_block = not in_code_block
            out_lines.append(line)
            i += 1
            continue
            
        if in_code_block:
            out_lines.append(line)
            i += 1
            continue

        if '|' in line and stripped.startswith('|') and stripped.endswith('|'):
            if in_quote_block:
                flush_quote()
            if re.match(r'^\s*\|(\s*:?-+:?\s*\|)+\s*$', stripped):
                i += 1
                continue
            cells = [c for c in stripped.strip('|').split('|')]
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            flush_table()
            
        if stripped.startswith('>'):
            if in_table:
                flush_table()
            in_quote_block = True
            quote_text = stripped.lstrip('>').strip()
            m_q_dm = re.search(r'___DISP_MATH_(\d+)___', quote_text)
            if m_q_dm:
                q_idx = int(m_q_dm.group(1))
                quote_text = quote_text.replace(f'___DISP_MATH_{q_idx}___', f' $ {disp_maths[q_idx]} $ ')
            if quote_text:
                quote_buffer.append(quote_text)
            i += 1
            continue
        elif in_quote_block and not stripped.startswith('>'):
            flush_quote()

        if stripped.startswith('#'):
            if in_quote_block:
                flush_quote()
            if in_table:
                flush_table()
            h_match = re.match(r'^(#+)\s*(.*)$', stripped)
            if h_match:
                level = len(h_match.group(1))
                h_text = format_inline(h_match.group(2))
                out_lines.append(f'{"=" * level} {h_text}\n')
                i += 1
                continue

        if stripped in ['---', '***', '___']:
            out_lines.append('#v(0.8em)\n#line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))\n#v(0.8em)\n')
            i += 1
            continue

        if re.match(r'^\s*[-*+]\s+', line):
            indent = len(line) - len(line.lstrip())
            indent_sp = " " * indent
            item_text = re.sub(r'^\s*[-*+]\s+', '', line)
            out_lines.append(f'{indent_sp}- {format_inline(item_text)}')
            i += 1
            continue

        if re.match(r'^\s*\d+\.\s+', line):
            indent = len(line) - len(line.lstrip())
            indent_sp = " " * indent
            item_text = re.sub(r'^\s*\d+\.\s+', '', line)
            out_lines.append(f'{indent_sp}+ {format_inline(item_text)}')
            i += 1
            continue

        if stripped:
            out_lines.append(format_inline(line))
        else:
            out_lines.append('')
            
        i += 1

    if in_quote_block:
        flush_quote()
    if in_table:
        flush_table()

    res = '\n'.join(out_lines)
    for idx, dm in enumerate(disp_maths):
        res = res.replace(f'___DISP_MATH_{idx}___', f' $ {dm} $ ')
        
    return res
