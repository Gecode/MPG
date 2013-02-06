#include <gecode/int.hh>
#include <gecode/minimodel.hh>

using namespace Gecode;

/**
 * \brief %Example: %Alpha puzzle
 *
 * Well-known cryptoarithmetic puzzle of unknown origin.
 *
 * \ingroup ExProblem
 *
 */
class Alpha : public Space {
protected:
  /// Alphabet has 26 letters
  static const int n = 26;
  /// Array for letters
  IntVarArray le;
public:
  /// Actual model
  Alpha(void) : le(*this,n,1,n) {
    IntVar
      a(le[ 0]), b(le[ 1]), c(le[ 2]), e(le[ 4]), f(le[ 5]),
      g(le[ 6]), h(le[ 7]), i(le[ 8]), j(le[ 9]), k(le[10]),
      l(le[11]), m(le[12]), n(le[13]), o(le[14]), p(le[15]),
      q(le[16]), r(le[17]), s(le[18]), t(le[19]), u(le[20]),
      v(le[21]), w(le[22]), x(le[23]), y(le[24]), z(le[25]);

    rel(*this, b+a+l+l+e+t       == 45);
    rel(*this, c+e+l+l+o         == 43);
    rel(*this, c+o+n+c+e+r+t     == 74);
    rel(*this, f+l+u+t+e         == 30);
    rel(*this, f+u+g+u+e         == 50);
    rel(*this, g+l+e+e           == 66);
    rel(*this, j+a+z+z           == 58);
    rel(*this, l+y+r+e           == 47);
    rel(*this, o+b+o+e           == 53);
    rel(*this, o+p+e+r+a         == 65);
    rel(*this, p+o+l+k+a         == 59);
    rel(*this, q+u+a+r+t+e+t     == 50);
    rel(*this, s+a+x+o+p+h+o+n+e == 134);
    rel(*this, s+c+a+l+e         == 51);
    rel(*this, s+o+l+o           == 37);
    rel(*this, s+o+n+g           == 61);
    rel(*this, s+o+p+r+a+n+o     == 82);
    rel(*this, t+h+e+m+e         == 72);
    rel(*this, v+i+o+l+i+n       == 100);
    rel(*this, w+a+l+t+z         == 34);

    distinct(*this, le);

    branch(*this, le, INT_VAR_NONE(), INT_VAL_MIN());
  }

  /// Constructor for cloning \a s
  Alpha(bool share, Alpha& s) : Space(share,s) {
    le.update(*this, share, s.le);
  }
  /// Copy during cloning
  virtual Space*
  copy(bool share) {
    return new Alpha(share,*this);
  }
  /// Print solution
  void
  print(std::ostream& os) const {
    os << "\t";
    for (int i = 0; i < n; i++) {
      os << ((char) (i+'a')) << '=' << le[i] << ((i<n-1)?", ":"\n");
      if ((i+1) % 8 == 0)
        os << std::endl << "\t";
    }
    os << std::endl;
  }
};

/** \brief Main-function
 *  \relates Alpha
 */
int
main(int argc, char* argv[]) {
  Alpha* a = new Alpha;
  if (Alpha* s = static_cast<Alpha*>(dfs(a)))
    s->print(std::cout);
  return 0;
}

// STATISTICS: example-any

