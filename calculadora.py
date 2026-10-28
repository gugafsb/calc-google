import collections
import os
import sys

try:
    import msvcrt
    def get_key():
        ch = msvcrt.getch()
        return ch.decode('utf-8', errors='ignore')
except ImportError:
    import termios
    import tty
    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

MAX_HISTORY = 20

history = collections.deque(maxlen=MAX_HISTORY)
undo_stack = []

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_num(val):
    if val is None:
        return ""
    if isinstance(val, float):
        return str(int(val)) if val.is_integer() else str(val)
    return str(val)

def get_float(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            val = float(raw)
            if abs(val) == float('inf') or val != val:
                print("Valor fora dos limites numéricos suportados. Tente novamente.")
                continue
            return val
        except (ValueError, OverflowError):
            print("Entrada inválida ou número fora dos limites. Tente novamente.")

def calculate(op, n1, n2):
    try:
        if op == 'a':
            res = n1 + n2
            symbol = '+'
        elif op == 's':
            res = n1 - n2
            symbol = '-'
        elif op == 'm':
            res = n1 * n2
            symbol = '*'
        elif op == 'd':
            if n2 == 0:
                print("Erro: Divisão por zero.")
                return None, None
            res = n1 / n2
            symbol = '/'
        elif op == 'p':
            res = (n1 * n2) / 100
            symbol = '%'
        else:
            return None, None

        if abs(res) == float('inf'):
            raise OverflowError

        return res, symbol
    except OverflowError:
        print("Erro: Operação excedeu os limites de precisão (double float).")
        return None, None

def show_history_mode():
    clear_screen()
    print("=== MODO HISTÓRICO ===")
    if not history:
        print("Memória vazia.")
    else:
        for item in history:
            print(item)
            print("--------------------")
    
    print("\n[Pressione 'h' para voltar]: ", end="", flush=True)
    while True:
        if get_key().lower() == 'h':
            clear_screen()
            break

def confirm_quit():
    while True:
        print("\nDeseja realmente sair? (S/N): ", end="", flush=True)
        resp = get_key().lower()
        print(resp)
        if resp == 's':
            sys.exit(0)
        elif resp == 'n':
            return False
        print("Opção inválida. Digite S ou N.")

def main():
    current_val = None

    while True:
        if current_val is None:
            print("\nEscolha [a: adição | s: subtração | m: multiplicação | d: divisão | p: porcentagem | h: histórico | q: sair]: ", end="", flush=True)
            cmd = get_key().lower()
            print(cmd)

            if cmd == 'q':
                confirm_quit()
                continue
            elif cmd == 'h':
                show_history_mode()
                continue
            elif cmd in ('a', 's', 'm', 'd', 'p'):
                prompt1 = "Digite o valor base: " if cmd == 'p' else "Digite o 1º número: "
                prompt2 = "Digite a porcentagem (%): " if cmd == 'p' else "Digite o 2º número: "
                n1 = get_float(prompt1)
                n2 = get_float(prompt2)
                res, sym = calculate(cmd, n1, n2)
                if res is not None:
                    undo_stack.append(current_val)
                    if len(undo_stack) > MAX_HISTORY:
                        undo_stack.pop(0)
                    history.append(f"{format_num(n1)} {sym} {format_num(n2)} = {format_num(res)}")
                    current_val = res
                    print(f"Resultado: {format_num(current_val)}")
            else:
                print("Opção inválida.")
        else:
            print(f"\nValor atual: {format_num(current_val)}\nEscolha [a: adição | s: subtração | m: multiplicação | d: divisão | p: porcentagem | h: histórico | u: desfazer | l: limpar | q: sair]: ", end="", flush=True)
            cmd = get_key().lower()
            print(cmd)

            if cmd == 'q':
                confirm_quit()
                continue
            elif cmd == 'h':
                show_history_mode()
                continue
            elif cmd == 'l':
                clear_screen()
                current_val = None
                undo_stack.clear()
                continue
            elif cmd == 'u':
                if undo_stack:
                    current_val = undo_stack.pop()
                    if history:
                        history.pop()
                    print("Última operação desfeita.")
                else:
                    print("Não há operações para desfazer.")
                continue
            elif cmd in ('a', 's', 'm', 'd', 'p'):
                prompt2 = "Digite a porcentagem (%): " if cmd == 'p' else "Digite o próximo número: "
                n2 = get_float(prompt2)
                res, sym = calculate(cmd, current_val, n2)
                if res is not None:
                    undo_stack.append(current_val)
                    if len(undo_stack) > MAX_HISTORY:
                        undo_stack.pop(0)
                    history.append(f"{format_num(current_val)} {sym} {format_num(n2)} = {format_num(res)}")
                    current_val = res
                    print(f"Resultado: {format_num(current_val)}")
                else:
                    print("Operação cancelada. Valor anterior mantido.")
            else:
                print("Opção inválida.")

if __name__ == "__main__":
    main()

    main()