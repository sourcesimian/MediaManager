#!/bin/sh

if [ "$1" = "complete" ]; then
    echo "install backup restore inspect"
    exit 0
fi

VOLUME=$(echo $DKRT_REPOTAG | cut -d: -f1 | tr '/' '_')


if ! docker inspect ${VOLUME} >/dev/null 2>&1; then
    docker volume create ${VOLUME}
fi

case "$1" in
    "install")
        { crontab -l | grep -v -e "# TAG:$DKRT_SCRIPT $DKRT_REPOTAG"; echo "* * * * * $DKRT_SCRIPT $DKRT_REPOTAG  # TAG:$DKRT_SCRIPT $DKRT_REPOTAG"; } | crontab -
        exit 0
        ;;
    "backup")
        TARGZ_FILE="${2:?[?TARGZ_FILE]}"
        OUTFILE=$(basename "$TARGZ_FILE")
        OUTDIR=$(cd "$(dirname "$TARGZ_FILE")"; echo $PWD)
        echo "Writing: $PWD/${OUTFILE}"
        exec docker run -it --rm \
        -v ${VOLUME}:/volume \
        -v ${OUTDIR}:/backup \
        alpine \
        tar -czf /backup/${OUTFILE} -C /volume ./
        ;;
    "restore")
        TARGZ_FILE="${2:?[?TARGZ_FILE]}"
        INFILE=$(basename "$TARGZ_FILE")
        INDIR=$(cd "$(dirname "$TARGZ_FILE")"; echo $PWD)
        echo "Restoring: ${INDIR}/${INFILE}"
        exec docker run -it --rm \
        -v ${VOLUME}:/volume \
        -v ${INDIR}:/backup \
        alpine \
        sh -c "rm -rf /volume/* /volume/..?* /volume/.[!.]* ; tar -C /volume/ -xzf /backup/${INFILE}"
        ;;
    "inspect")
        exec docker run -it --rm \
        -v ${VOLUME}:/cache \
        ${DKRT_REPOTAG} \
        /bin/sh
        ;;
esac

for pid in $(ps aux | grep "[d]ocker run .* ${DKRT_REPOTAG}" | awk '{print $2}'); do
    if strings /proc/$pid/environ 2>/dev/null | grep -q "DKRT=${DKRT_REPOTAG}"; then
        echo "Already running"
        exit 0
    fi
done


user_id()
{
    case "$OSTYPE" in
        linux*)
            echo "$(id -u):$(id -g)"
        ;;
        darwin*)
            echo "$(id -u)"
        ;;
        *)
            echo "$(id -u):$(id -g)"
        ;;
    esac
}


export DKRT=${DKRT_REPOTAG}
exec docker run -it --rm \
    -v ${VOLUME}:/cache:rw \
    -v $HOME:$HOME:rw \
    -v /mnt:/mnt:rw \
    --workdir ${PWD} \
    --user "$(user_id)" \
    ${DKRT_REPOTAG} \
     /cli.sh --cache /cache "$@"
