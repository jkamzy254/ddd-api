# Register Microsoft ODBC Driver 18 (installed by the apt buildpack under /app/.apt)
# so unixODBC can find it by name: "ODBC Driver 18 for SQL Server".
# Heroku runs this at dyno startup.
MSODBC18_LIB=$(ls /app/.apt/opt/microsoft/msodbcsql18/lib64/libmsodbcsql-18.*.so.* 2>/dev/null | head -n 1)

if [ -n "$MSODBC18_LIB" ]; then
  mkdir -p /app/.odbc
  cat > /app/.odbc/odbcinst.ini <<EOF
[ODBC Driver 18 for SQL Server]
Description=Microsoft ODBC Driver 18 for SQL Server
Driver=$MSODBC18_LIB
UsageCount=1
EOF
  export ODBCSYSINI=/app/.odbc
else
  echo "msodbcsql18.sh: ODBC Driver 18 library not found under /app/.apt" >&2
fi
