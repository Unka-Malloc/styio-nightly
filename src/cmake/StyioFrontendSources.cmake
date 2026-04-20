set(STYIO_FRONTEND_FOUNDATION_SOURCES
  StyioToken/Token.cpp
  StyioUnicode/Unicode.cpp
  StyioParser/Parser.cpp
  StyioParser/ParserLookahead.cpp
  StyioParser/SymbolRegistry.cpp
  StyioParser/NewParserExpr.cpp
  StyioParser/Tokenizer.cpp
)

set(STYIO_FRONTEND_SEMA_IR_SOURCES
  StyioToString/ToString.cpp
  StyioAnalyzer/TypeInfer.cpp
  StyioAnalyzer/ToStyioIR.cpp
)

set(STYIO_FRONTEND_SOURCES
  ${STYIO_FRONTEND_FOUNDATION_SOURCES}
  ${STYIO_FRONTEND_SEMA_IR_SOURCES}
)
