# Python Reference Traceability Matrix

Each row is a leaf section from the Python Language Reference.
The **Ref** column uses the format `file.section[.subsection[.subsubsection]]`.

| Ref | Section Title | Tested By | Status |
|-----|---------------|-----------|--------|
| 1.1 | Alternate Implementations | 0001, 0219, 0220 | PASS |
| 1.2.1 | Lexical and Syntactic definitions | 0002, 0221, 0222 | PASS |
| 2.1.1 | Logical lines | 0003, 0223, 0224 | PASS |
| 2.1.2 | Physical lines | 0004, 0225, 0226 | PASS |
| 2.1.3 | Comments | 0005, 0227, 0228 | PASS |
| 2.1.4 | Encoding declarations | 0006, 0229, 0230 | PASS |
| 2.1.5 | Explicit line joining | 0007, 0231, 0232 | PASS |
| 2.1.6 | Implicit line joining | 0008, 0233, 0234 | PASS |
| 2.1.7 | Blank lines | 0009, 0235, 0236 | PASS |
| 2.1.8 | Indentation | 0010, 0237, 0238 | PASS |
| 2.1.9 | Whitespace between tokens | 0011, 0239, 0240 | PASS |
| 2.1.10 | End marker | 0012, 0241, 0242 | PASS |
| 2.2 | Other tokens | 0013, 0243, 0244 | PASS |
| 2.3.1 | Keywords | 0014, 0245, 0246 | PASS |
| 2.3.2 | Soft Keywords | 0015 | UNSUPPORTED |
| 2.3.3 | Reserved classes of identifiers | 0016, 0247, 0248 | PASS |
| 2.3.4 | Non-ASCII characters in names | 0017 | UNSUPPORTED |
| 2.4 | Literals | 0018, 0249, 0250 | PASS |
| 2.5.1 | Triple-quoted strings | 0019, 0251, 0252 | PASS |
| 2.5.2 | String prefixes | 0020, 0253, 0254 | PASS |
| 2.5.3 | Formal grammar | 0021, 0255, 0256 | PASS |
| 2.5.4.1 | Ignored end of line | 0022, 0257, 0258 | PASS |
| 2.5.4.2 | Escaped characters | 0023, 0259, 0260 | PASS |
| 2.5.4.3 | Octal character | 0024, 0261, 0262 | PASS |
| 2.5.4.4 | Hexadecimal character | 0025, 0263, 0264 | PASS |
| 2.5.4.5 | Named Unicode character | 0026, 0265, 0266 | PASS |
| 2.5.4.6 | Hexadecimal Unicode characters | 0027, 0267, 0268 | PASS |
| 2.5.4.7 | Unrecognized escape sequences | 0028, 0269, 0270 | PASS |
| 2.5.5 | Bytes literals | 0029, 0271, 0272 | PASS |
| 2.5.6 | Raw string literals | 0030, 0273, 0274 | PASS |
| 2.5.7 | f-strings | 0031, 0275, 0276 | PASS |
| 2.5.8 | t-strings | 0032, 0277, 0278 | PASS |
| 2.5.9 | Formal grammar for f-strings | 0033, 0279, 0280 | PASS |
| 2.6.1 | Integer literals | 0034, 0281, 0282 | PASS |
| 2.6.2 | Floating-point literals | 0035, 0283, 0284 | PASS |
| 2.6.3 | Imaginary literals | 0036, 0285, 0286 | PASS |
| 2.7 | Operators and delimiters | 0037, 0287, 0288 | PASS |
| 3.1 | Objects, values and types | 0038, 0289, 0290 | PASS |
| 3.2.1 | None | 0039 | UNSUPPORTED |
| 3.2.2 | NotImplemented | 0040 | UNSUPPORTED |
| 3.2.3 | Ellipsis | 0041 | UNSUPPORTED |
| 3.2.4.1 | :class:`numbers.Integral` | 0042, 0291, 0292 | PASS |
| 3.2.4.2 | :class:`numbers.Real` (:class:`float`) | 0043 | UNSUPPORTED |
| 3.2.4.3 | :class:`numbers.Complex` (:class:`complex`) | 0044 | UNSUPPORTED |
| 3.2.5.1 | Immutable sequences | 0045 | UNSUPPORTED |
| 3.2.5.2 | Mutable sequences | 0046 | UNSUPPORTED |
| 3.2.6 | Set types | 0047 | UNSUPPORTED |
| 3.2.7.1 | Dictionaries | 0048 | UNSUPPORTED |
| 3.2.8.1.1 | Special read-only attributes | 0049 | UNSUPPORTED |
| 3.2.8.1.2 | Special writable attributes | 0050 | UNSUPPORTED |
| 3.2.8.2 | Instance methods | 0051, 0293, 0294 | PASS |
| 3.2.8.3 | Generator functions | 0052, 0295, 0296 | PASS |
| 3.2.8.4 | Coroutine functions | 0053, 0297, 0298 | PASS |
| 3.2.8.5 | Asynchronous generator functions | 0054, 0299, 0300 | PASS |
| 3.2.8.6 | Built-in functions | 0055, 0301, 0302 | PASS |
| 3.2.8.7 | Built-in methods | 0056, 0303, 0304 | PASS |
| 3.2.8.8 | Classes | 0057, 0305, 0306 | PASS |
| 3.2.8.9 | Class Instances | 0058, 0307, 0308 | PASS |
| 3.2.9.1 | Import-related attributes on module objects | 0059 | UNSUPPORTED |
| 3.2.9.2 | Other writable attributes on module objects | 0060 | UNSUPPORTED |
| 3.2.9.3 | Module dictionaries | 0061 | UNSUPPORTED |
| 3.2.10.1 | Special attributes | 0062, 0309, 0310 | PASS |
| 3.2.10.2 | Special methods | 0063, 0311, 0312 | PASS |
| 3.2.11.1 | Special attributes | 0064, 0313, 0314 | PASS |
| 3.2.12 | I/O objects (also known as file objects) | 0065, 0315, 0316 | PASS |
| 3.2.13.1.1 | Special read-only attributes | 0066, 0317, 0318 | PASS |
| 3.2.13.1.2 | Methods on code objects | 0067, 0319, 0320 | PASS |
| 3.2.13.2.1 | Special read-only attributes | 0068, 0321, 0322 | PASS |
| 3.2.13.2.2 | Special writable attributes | 0069, 0323, 0324 | PASS |
| 3.2.13.2.3 | Frame object methods | 0070, 0325, 0326 | PASS |
| 3.2.13.3 | Traceback objects | 0071, 0327, 0328 | PASS |
| 3.2.13.4 | Slice objects | 0072, 0329, 0330 | PASS |
| 3.2.13.5 | Static method objects | 0073, 0331, 0332 | PASS |
| 3.2.13.6 | Class method objects | 0074, 0333, 0334 | PASS |
| 3.3.1 | Basic customization | 0075 | UNSUPPORTED |
| 3.3.2.1 | Customizing module attribute access | 0076 | UNSUPPORTED |
| 3.3.2.2 | Implementing Descriptors | 0077, 0335, 0336 | PASS |
| 3.3.2.3 | Invoking Descriptors | 0078 | UNSUPPORTED |
| 3.3.2.4 | __slots__ | 0079 | UNSUPPORTED |
| 3.3.3.1 | Metaclasses | 0080, 0337, 0338 | PASS |
| 3.3.3.2 | Resolving MRO entries | 0081, 0339, 0340 | PASS |
| 3.3.3.3 | Determining the appropriate metaclass | 0082, 0341, 0342 | PASS |
| 3.3.3.4 | Preparing the class namespace | 0083, 0343, 0344 | PASS |
| 3.3.3.5 | Executing the class body | 0084, 0345, 0346 | PASS |
| 3.3.3.6 | Creating the class object | 0085, 0347, 0348 | PASS |
| 3.3.3.7 | Uses for metaclasses | 0086, 0349, 0350 | PASS |
| 3.3.4 | Customizing instance and subclass checks | 0087 | UNSUPPORTED |
| 3.3.5.1 | The purpose of *__class_getitem__* | 0088, 0351, 0352 | PASS |
| 3.3.5.2 | *__class_getitem__* versus *__getitem__* | 0089, 0353, 0354 | PASS |
| 3.3.6 | Emulating callable objects | 0090, 0355, 0356 | PASS |
| 3.3.7 | Emulating container types | 0091 | UNSUPPORTED |
| 3.3.8 | Emulating numeric types | 0092 | UNSUPPORTED |
| 3.3.9 | With Statement Context Managers | 0093, 0357, 0358 | PASS |
| 3.3.10 | Customizing positional arguments in class pattern matching | 0094, 0359, 0360 | PASS |
| 3.3.11 | Emulating buffer types | 0095 | UNSUPPORTED |
| 3.3.12 | Annotations | 0096, 0361, 0362 | PASS |
| 3.3.13 | Special method lookup | 0097, 0363, 0364 | PASS |
| 3.4.1 | Awaitable Objects | 0098, 0365, 0366 | PASS |
| 3.4.2 | Coroutine Objects | 0099 | UNSUPPORTED |
| 3.4.3 | Asynchronous Iterators | 0100, 0367, 0368 | PASS |
| 3.4.4 | Asynchronous Context Managers | 0101, 0369, 0370 | PASS |
| 4.1 | Structure of a program | 0102, 0371, 0372 | PASS |
| 4.2.1 | Binding of names | 0103, 0373, 0374 | PASS |
| 4.2.2 | Resolution of names | 0104, 0375, 0376 | PASS |
| 4.2.3 | Annotation scopes | 0105, 0377, 0378 | PASS |
| 4.2.4 | Lazy evaluation | 0106, 0379, 0380 | PASS |
| 4.2.5 | Builtins and restricted execution | 0107, 0381, 0382 | PASS |
| 4.2.6 | Interaction with dynamic features | 0108, 0383, 0384 | PASS |
| 4.3 | Exceptions | 0109, 0385, 0386 | PASS |
| 4.4.1 | General Computing Model | 0110 | UNSUPPORTED |
| 4.4.2 | Python Runtime Model | 0111, 0387, 0388 | PASS |
| 5.1 | :mod:`importlib` | 0112, 0389, 0390 | PASS |
| 5.2.1 | Regular packages | 0113, 0391, 0392 | PASS |
| 5.2.2 | Namespace packages | 0114, 0393, 0394 | PASS |
| 5.3.1 | The module cache | 0115, 0395, 0396 | PASS |
| 5.3.2 | Finders and loaders | 0116, 0397, 0398 | PASS |
| 5.3.3 | Import hooks | 0117, 0399, 0400 | PASS |
| 5.3.4 | The meta path | 0118, 0401, 0402 | PASS |
| 5.4.1 | Loaders | 0119, 0403, 0404 | PASS |
| 5.4.2 | Submodules | 0120, 0405, 0406 | PASS |
| 5.4.3 | Module specs | 0121, 0407, 0408 | PASS |
| 5.4.4 | __path__ attributes on modules | 0122, 0409, 0410 | PASS |
| 5.4.5 | Module reprs | 0123, 0411, 0412 | PASS |
| 5.4.6 | Cached bytecode invalidation | 0124, 0413, 0414 | PASS |
| 5.5.1 | Path entry finders | 0125, 0415, 0416 | PASS |
| 5.5.2 | Path entry finder protocol | 0126, 0417, 0418 | PASS |
| 5.6 | Replacing the standard import system | 0127, 0419, 0420 | PASS |
| 5.7 | Package Relative Imports | 0128, 0421, 0422 | PASS |
| 5.8.1 | __main__.__spec__ | 0129, 0423, 0424 | PASS |
| 5.9 | References | 0130, 0425, 0426 | PASS |
| 6.1 | Arithmetic conversions | 0131 | UNSUPPORTED |
| 6.2.1 | Built-in constants | 0132, 0427, 0428 | PASS |
| 6.2.2.1 | Private name mangling | 0133, 0429, 0430 | PASS |
| 6.2.3.1 | Literals and object identity | 0134, 0431, 0432 | PASS |
| 6.2.3.2 | String literal concatenation | 0135, 0433, 0434 | PASS |
| 6.2.4 | Parenthesized forms | 0136 | UNSUPPORTED |
| 6.2.5 | Displays for lists, sets and dictionaries | 0137 | UNSUPPORTED |
| 6.2.6 | List displays | 0138 | UNSUPPORTED |
| 6.2.7 | Set displays | 0139 | UNSUPPORTED |
| 6.2.8 | Dictionary displays | 0140 | UNSUPPORTED |
| 6.2.9 | Generator expressions | 0141 | UNSUPPORTED |
| 6.2.10.1 | Generator-iterator methods | 0142, 0435, 0436 | PASS |
| 6.2.10.2 | Examples | 0143, 0437, 0438 | PASS |
| 6.2.10.3 | Asynchronous generator functions | 0144, 0439, 0440 | PASS |
| 6.2.10.4 | Asynchronous generator-iterator methods | 0145, 0441, 0442 | PASS |
| 6.3.1 | Attribute references | 0146 | UNSUPPORTED |
| 6.3.2.1 | Slicings | 0147 | UNSUPPORTED |
| 6.3.2.2 | Comma-separated subscripts | 0148, 0443, 0444 | PASS |
| 6.3.2.3 | "Starred" subscriptions | 0149, 0445, 0446 | PASS |
| 6.3.2.4 | Formal subscription grammar | 0150, 0447, 0448 | PASS |
| 6.3.3 | Calls | 0151 | UNSUPPORTED |
| 6.4 | Await expression | 0152, 0449, 0450 | PASS |
| 6.5 | The power operator | 0153 | UNSUPPORTED |
| 6.6 | Unary arithmetic and bitwise operations | 0154, 0451, 0452 | PASS |
| 6.7 | Binary arithmetic operations | 0155, 0453, 0454 | PASS |
| 6.8 | Shifting operations | 0156 | UNSUPPORTED |
| 6.9 | Binary bitwise operations | 0157 | UNSUPPORTED |
| 6.10.1 | Value comparisons | 0158, 0455, 0456 | PASS |
| 6.10.2 | Membership test operations | 0159 | UNSUPPORTED |
| 6.10.3 | Identity comparisons | 0160 | UNSUPPORTED |
| 6.11 | Boolean operations | 0161 | UNSUPPORTED |
| 6.12 | Assignment expressions | 0162 | UNSUPPORTED |
| 6.13 | Conditional expressions | 0163 | UNSUPPORTED |
| 6.14 | Lambdas | 0164 | UNSUPPORTED |
| 6.15 | Expression lists | 0165 | UNSUPPORTED |
| 6.16 | Evaluation order | 0166 | UNSUPPORTED |
| 6.17 | Operator precedence | 0167, 0457, 0458 | PASS |
| 7.1 | Expression statements | 0168, 0459, 0460 | PASS |
| 7.2.1 | Augmented assignment statements | 0169, 0461, 0462 | PASS |
| 7.2.2 | Annotated assignment statements | 0170 | UNPROVEN |
| 7.3 | The :keyword:`!assert` statement | 0171, 0463, 0464 | PASS |
| 7.4 | The :keyword:`!pass` statement | 0172, 0465, 0466 | PASS |
| 7.5 | The :keyword:`!del` statement | 0173, 0467, 0468 | PASS |
| 7.6 | The :keyword:`!return` statement | 0174, 0469, 0470 | PASS |
| 7.7 | The :keyword:`!yield` statement | 0175 | UNSUPPORTED |
| 7.8 | The :keyword:`!raise` statement | 0176 | UNSUPPORTED |
| 7.9 | The :keyword:`!break` statement | 0177 | UNSUPPORTED |
| 7.10 | The :keyword:`!continue` statement | 0178 | UNSUPPORTED |
| 7.11.1.1 | Compatibility via ``__lazy_modules__`` | 0179, 0471, 0472 | PASS |
| 7.11.2 | Future statements | 0180, 0473, 0474 | PASS |
| 7.12 | The :keyword:`!global` statement | 0181, 0475, 0476 | PASS |
| 7.13 | The :keyword:`!nonlocal` statement | 0182 | UNSUPPORTED |
| 7.14 | The :keyword:`!type` statement | 0183, 0477, 0478 | PASS |
| 8.1 | The :keyword:`!if` statement | 0184, 0479, 0480 | PASS |
| 8.2 | The :keyword:`!while` statement | 0185 | UNSUPPORTED |
| 8.3 | The :keyword:`!for` statement | 0186 | UNPROVEN |
| 8.4.1 | :keyword:`!except` clause | 0187 | UNSUPPORTED |
| 8.4.2 | :keyword:`!except*` clause | 0188, 0481, 0482 | PASS |
| 8.4.3 | :keyword:`!else` clause | 0189, 0483, 0484 | PASS |
| 8.4.4 | :keyword:`!finally` clause | 0190, 0485, 0486 | PASS |
| 8.5 | The :keyword:`!with` statement | 0191, 0487, 0488 | PASS |
| 8.6.1 | Overview | 0192 | UNSUPPORTED |
| 8.6.2 | Guards | 0193 | UNSUPPORTED |
| 8.6.3 | Irrefutable Case Blocks | 0194 | UNSUPPORTED |
| 8.6.4.1 | OR Patterns | 0195 | UNSUPPORTED |
| 8.6.4.2 | AS Patterns | 0196 | UNSUPPORTED |
| 8.6.4.3 | Literal Patterns | 0197 | UNSUPPORTED |
| 8.6.4.4 | Capture Patterns | 0198 | UNSUPPORTED |
| 8.6.4.5 | Wildcard Patterns | 0199 | UNSUPPORTED |
| 8.6.4.6 | Value Patterns | 0200 | UNSUPPORTED |
| 8.6.4.7 | Group Patterns | 0201 | UNSUPPORTED |
| 8.6.4.8 | Sequence Patterns | 0202 | UNSUPPORTED |
| 8.6.4.9 | Mapping Patterns | 0203 | UNSUPPORTED |
| 8.6.4.10 | Class Patterns | 0204 | UNSUPPORTED |
| 8.7 | Function definitions | 0205 | UNSUPPORTED |
| 8.8.1 | Multiple inheritance | 0206, 0489, 0490 | PASS |
| 8.9.1 | Coroutine function definition | 0207, 0491, 0492 | PASS |
| 8.9.2 | The :keyword:`!async for` statement | 0208, 0493, 0494 | PASS |
| 8.9.3 | The :keyword:`!async with` statement | 0209, 0495, 0496 | PASS |
| 8.10.1 | Generic functions | 0210, 0497, 0498 | PASS |
| 8.10.2 | Generic classes | 0211 | UNSUPPORTED |
| 8.10.3 | Generic type aliases | 0212, 0499, 0500 | PASS |
| 8.11 | Annotations | 0213, 0501, 0502 | PASS |
| 9.1 | Complete Python programs | 0214, 0503, 0504 | PASS |
| 9.2 | File input | 0215, 0505, 0506 | PASS |
| 9.3 | Interactive input | 0216, 0507, 0508 | PASS |
| 9.4 | Expression input | 0217 | UNSUPPORTED |
| 10.1 | Full Grammar specification | 0218, 0509, 0510 | PASS |
