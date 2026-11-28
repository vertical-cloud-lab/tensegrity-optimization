# strip-todos.awk: remove every \todo[opt]{arg} from a LaTeX file.
#
# Usage: gawk -f strip-todos.awk file.tex > out.tex
#
# The argument may span lines and contain nested braces. A line that the
# removal leaves empty is deleted, so no paragraph break appears where the
# note stood. If the deleted line followed a line ending in "%", that "%"
# is dropped too, so the line break that separated the words around the
# note still yields a space.
BEGIN { RS = "^$" }
{
  s = $0; n = length(s); out = ""; i = 1
  while (i <= n) {
    if (substr(s, i, 5) == "\\todo" && substr(s, i + 5, 1) !~ /[A-Za-z]/) {
      j = i + 5
      if (substr(s, j, 1) == "[") {
        depth = 1; j++
        while (j <= n && depth > 0) {
          c = substr(s, j, 1)
          if (c == "[") depth++
          else if (c == "]") depth--
          j++
        }
      }
      if (substr(s, j, 1) == "{") {
        depth = 1; j++
        while (j <= n && depth > 0) {
          c = substr(s, j, 1)
          if (c == "\\") { j += 2; continue }
          if (c == "{") depth++
          else if (c == "}") depth--
          j++
        }
        out = out "\001"
        i = j
        continue
      }
    }
    out = out substr(s, i, 1); i++
  }
  m = split(out, L, "\n"); kept = 0
  for (k = 1; k <= m; k++) {
    line = L[k]
    if (index(line, "\001") > 0) {
      t = line; gsub(/\001/, "", t)
      if (t ~ /^[ \t]*$/) {
        if (kept > 0 && K[kept] ~ /[^\\]%$/) sub(/%$/, "", K[kept])
        continue
      }
      line = t
    }
    K[++kept] = line
  }
  for (k = 1; k <= kept; k++) printf "%s%s", K[k], (k < kept ? "\n" : "")
}
