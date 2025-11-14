
if [ $# -le 0 ]; then
    echo "usage: filelist"
    exit;
fi

cat ${@} \
    | awk '{print "soxi -D " $2}' \
    | sh \
    | awk '{sum+=$1; print sum/3600}' \
    | tail -n 1
