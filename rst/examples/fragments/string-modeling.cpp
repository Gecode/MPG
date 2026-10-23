#include <gecode/string.hh>

using namespace Gecode;

String::StringVal greeting =
  String::StringVal::from_symbols({0x65E5, 0x672C, 0x1F600});
StringVar fixed(home, greeting);
StringVar word(home, 0, 12, String::StringAlphabet::unicode_scalars());

IntVar size(home, 0, 12);
length(home, word, size);
extensional(home, word, "(\\u{65E5}|\\u{672C}|\\u{1F600})(\\u{65E5}|\\u{672C}|\\u{1F600})*");
rel(home, word, STRT_NQ, fixed);

StringVarArgs strings(1);
strings[0] = word;
branch(home, strings, STRING_VAR_SIZEMIN(), STRING_VAL_LLUL());

StringVar sentence(home, "a cat and a dog");
IntVar first_match(home, 0, sentence.max_length());
match(home, sentence, "(cat|dog)", first_match);

String::NSBlocks blocks;
blocks.push_back(String::NSBlock(String::NSIntSet('a', 'b'), 1, 2));
blocks.push_back(String::NSBlock(String::NSIntSet('0', '1'), 1, 2));
StringVar code(home, blocks, 3, 3);

StringVar source(home, "abcde");
StringVar slice(home, 0, 5);
substr(home, source, IntVar(home, 2, 2), IntVar(home, 4, 4), slice);

BoolVar member(home, 0, 1);
extensional(home, word, "(ab)*", member, RM_EQV);

StringVarArray words(home, 2);
for (int i = 0; i < words.size(); ++i)
  words[i] = StringVar(home, 1, 4, String::StringAlphabet::ascii());
