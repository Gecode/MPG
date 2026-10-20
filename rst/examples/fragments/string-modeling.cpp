#include <gecode/string.hh>

using namespace Gecode;

String::StringVal greeting =
  String::StringVal::from_symbols({0x65E5, 0x672C, 0x1F600});
StringVar fixed(home, greeting);
StringVar word(home, 0, 12, String::StringAlphabet::unicode_scalars());

IntVar size(home, 0, 12);
length(home, word, size);
extensional(home, word, "(\\u{65E5}|\\u{672C}|\\u{1F600})+");
rel(home, word, STRT_NQ, fixed);

StringVarArgs strings(1);
strings[0] = word;
branch(home, strings, STRING_VAR_SIZEMIN(), STRING_VAL_LLLL());
