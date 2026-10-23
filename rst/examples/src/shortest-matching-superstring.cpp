#include <gecode/string.hh>
#include <gecode/search.hh>
#include <gecode/minimodel.hh>

#include <iostream>
#include <memory>
#include <utility>

using namespace Gecode;

class ShortestMatchingSuperstring : public IntMinimizeSpace {
public:
  StringVar text;
  IntVar size;

  ShortestMatchingSuperstring(void)
    : text(*this, 0, 10,
           String::StringAlphabet::from_codepoints(
             {'a', 'b', 'c', 'd', 'e', 'f'})),
      size(*this, 0, 10) {
    const char* patterns[] = {"ab(c|d)", "(c|d)ef", "efab"};
    length(*this, text, size);
    for (const char* pattern : patterns) {
      IntVar first(*this, 1, 10);
      match(*this, text, pattern, first);
    }
    branch(*this, size, INT_VAL_MIN());
    StringVarArgs strings(1);
    strings[0] = text;
    branch(*this, strings, STRING_VAR_NONE(), STRING_VAL_LLLL());
  }

  ShortestMatchingSuperstring(ShortestMatchingSuperstring& other)
    : IntMinimizeSpace(other) {
    text.update(*this, other.text);
    size.update(*this, other.size);
  }

  virtual Space* copy(void) {
    return new ShortestMatchingSuperstring(*this);
  }

  virtual IntVar cost(void) const {
    return size;
  }
};

int main(void) {
  std::unique_ptr<ShortestMatchingSuperstring> model(
    new ShortestMatchingSuperstring);
  BAB<ShortestMatchingSuperstring> search(model.get());
  model.reset();
  std::unique_ptr<ShortestMatchingSuperstring> best;
  while (std::unique_ptr<ShortestMatchingSuperstring> solution{search.next()})
    best = std::move(solution);
  if (!best) {
    std::cerr << "No matching superstring within the length bound\n";
    return 1;
  }
  std::cout << best->text.val_symbols().to_utf8()
            << " length=" << best->size.val() << '\n';
  return 0;
}
