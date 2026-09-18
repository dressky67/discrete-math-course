PREAMBLE = '''#set page(
  paper: "a4",
  margin: (x: 2cm, top: 2.5cm, bottom: 2.5cm),
  header: align(right)[_Дискретная математика и основы теории матриц_],
  footer: align(center)[#context counter(page).display()]
)
#set text(
  font: ("Times New Roman", "Cambria"),
  size: 10.5pt,
  lang: "ru"
)
#set par(justify: true, leading: 0.65em)
#set heading(numbering: "1.1.")

#let land = sym.and
#let lor = sym.or
#let cap = sym.inter
#let cup = sym.union
#let cdot = sym.dot
#let oplus = [⊕]
#let odot = [⊙]
#let times = sym.times
#let approx = sym.approx
#let equiv = sym.equiv
#let neq = sym.eq.not
#let le = sym.lt.eq
#let ge = sym.gt.eq
#let subseteq = sym.subset.eq
#let emptyset = sym.nothing
#let infty = sym.infinity
#let pmod(n) = [(mod #n)]
#let RR = math.bb("R")
#let NN = math.bb("N")
#let ZZ = math.bb("Z")
#let QQ = math.bb("Q")
#let FF = math.bb("F")
#let CC = math.bb("C")
#let circ = sym.compose
#let implies = sym.arrow.r.double
#let impliedby = sym.arrow.l.double
#let iff = sym.arrow.l.r.double
#let leftarrow = sym.arrow.l
#let rightarrow = sym.arrow.r
#let to = sym.arrow.r

#let ij = $i j$
#let ii = $i i$
#let jj = $j j$
#let kk = $k k$
#let ik = $i k$
#let kj = $k j$
#let jk = $j k$
#let ji = $j i$
#let ad = $a d$
#let bc = $b c$
#let ab = $a b$
#let ba = $b a$
#let cd = $c d$
#let dc = $d c$
#let cb = $c b$
#let da = $d a$
#let ax = $a x$
#let yx = $y x$
#let xy = $x y$
#let yz = $y z$
#let zx = $z x$
#let xz = $x z$
#let xyz = $x y z$
#let dx = $d x$
#let dy = $d y$
#let dz = $d z$
#let ak = $a k$
#let bm = $b m$
#let km = $k m$
#let pq = $p q$
#let qp = $q p$
#let qr = $q r$
#let uv = $u v$
#let vu = $v u$
#let st = $s t$
#let ts = $t s$
#let mn = $m n$
#let nm = $n m$
#let ed = $e d$
#let de = $d e$
#let AB = $A B$
#let BA = $B A$
#let AC = $A C$
#let BC = $B C$
#let CD = $C D$
#let DA = $D A$
#let PQ = $P Q$
#let QP = $Q P$
#let tr = math.op("tr")
#let rref = math.op("rref")
#let rank = math.op("rank")
#let diag = math.op("diag")
#let span = math.op("span")
'''
