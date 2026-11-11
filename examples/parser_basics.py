"""学习演示：观察现有 Parser 的 token 操作，不新增语言规则。

在项目根目录运行：python3 -m examples.parser_basics
"""
from klean import Parser
from klean.lexer_adapter import tokenize
from klean.parser import ParseError


def show(parser, label):
    token = parser.current
    print(f'{label}: position={parser.position}, '
          f'kind={token.kind!r}, text={token.text!r}, '
          f'位置={token.line}:{token.column}')


def main():
    tokens, errors = tokenize('print(23);')
    assert not errors
    parser = Parser(tokens)
    print('一、查看、消费、检查并消费')
    show(parser, '初始状态')
    print('查看 current：', parser.current)
    show(parser, '查看后（位置不变）')
    print('take 返回：', parser.take())
    show(parser, '消费 print 后')
    print("expect('(') 返回：", parser.expect('('))
    show(parser, '匹配左括号后')

    print('\n二、匹配失败时的位置与错误')
    try:
        parser.expect(')')  # 当前是数字 23，故意要求右括号。
    except ParseError:
        error = parser.diagnostics[-1]
        print(f'{error.line}:{error.column}: {error.message}')
    show(parser, '匹配失败后（位置不变）')

    print('\n三、从头解析同一串 tokens，得到 AST')
    result = Parser(tokens).parse()  # 新实例从 position=0 开始。
    print(result.program)
    print('语法错误：', result.diagnostics)


if __name__ == '__main__':
    main()
