#!"C:\Program Files\Git\bin\bash"

set -e

while getopts ":c:e:r:" opt; do
    case $opt in
        c)
            TICKER=$OPTARG
            ;;
        e)
            PRICE=$OPTARG
            ;;
        r)
            USER=$OPTARG
            ;;

    esac
done




#which python3
python3 api_polling.py $TICKER $PRICE $USER
