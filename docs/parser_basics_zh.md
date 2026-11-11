# Parser 入门：截图中的三个操作

这份自学说明配合项目现有的 `klean/parser.py`，帮助你读懂代码。
截图中的第一步已经在现有 Parser 中实现，可以直接运行演示观察。

## 运行

在终端进入项目目录，再运行：

```sh
cd /Users/yoyo/Documents/LM
python3 -m examples.parser_basics
```

演示使用 `print(23);`，它的 token 序列是：

| 下标 | kind | text |
| --- | --- | --- |
| 0 | print | print |
| 1 | ( | ( |
| 2 | INT_LIT | 23 |
| 3 | ) | ) |
| 4 | ; | ; |
| 5 | EOF | 空字符串 |

`position` 是当前 token 的下标，从 0 开始。`line`、`column` 是源代码中的位置，从 1 开始。EOF 表示输入结束；当前实现要求 token 列表末尾有且仅有一个 EOF。

## 三个基本操作

| 截图中的操作 | 现有接口 | 成功时的位置变化 |
| --- | --- | --- |
| 查看当前 token | `parser.current` | 不移动 |
| 消费当前 token | `parser.take()` | 前进一格；EOF 时停留原地 |
| 检查并消费指定类型 | `parser.expect(kind)` | 匹配成功时消费；失败时不移动并报错 |

`current` 使用了 `@property`，因此读取时不加括号。
`take()` 返回移动前的 token，调用方仍可以读取刚消费的内容。
`expect('INT_LIT')` 检查的是 token 的 `kind`，不是数字文本 `'23'`。

运行演示时，位置依次是：

1. 初始 `position=0`，当前是 `print`。
2. 读取 `current` 后仍为 0。
3. `take()` 返回 `print`，位置变为 1，当前是左括号。
4. `expect('(')` 成功，位置变为 2，当前是数字 `23`。
5. 此时故意调用 `expect(')')`，得到第 1 行第 7 列的错误，位置仍为 2。

失败时，`expect()` 调用 `fail()`：先把行、列和错误文字放入 `diagnostics`，再抛出 `ParseError`。演示捕获异常以便继续展示；完整解析流程则由 `items()` 捕获异常，并尝试跳过出错部分、继续解析后面的语句。

代码还有一个辅助方法 `accept(kind)`：匹配就消费并返回 token，不匹配就返回 `None`，不报错。它适合检查可选语法；`expect()` 适合检查必须出现的语法。

## tokens 怎样变成 AST

对于 `print(23);`，现有解析路径是：

```text
parse() → items() → statement()
                     ├─ 消费 print
                     ├─ 要求 (
                     ├─ expression() → … → factor() → Integer
                     ├─ 要求 )
                     └─ 要求 ; → Print
```

最终树的主要结构是：

```text
Program
└─ Print
   └─ Integer(decimal='23')
```

`Parser(tokens).parse()` 返回 `ParseResult`，其中 `program` 是 AST，`diagnostics` 是语法错误列表。Lexer 的错误由 `tokenize()` 单独返回；使用 AST 前应同时检查两者。AST 描述程序结构，这一步不会执行 `print`，也不会计算表达式的值。

演示最后用新的 `Parser(tokens)` 从头解析，因为前面的手动操作已经移动了旧实例的位置。

## 截图中的 32 位整数提醒

有符号 32 位整数范围是 `-2147483648` 到 `2147483647`。当前 Parser 将整数字面量的十进制文本保存在 AST 中；它不负责检查这个范围。后续语义分析和运行阶段还需要按组内确定的规则处理越界、溢出以及负数最小值。

阅读时可以自行验证：连续读取两次 `current` 是否移动位置；在 EOF 上调用 `take()` 是否越界；把演示中的 `expect(')')` 改为 `expect('INT_LIT')` 后，当前位置会变成什么。
