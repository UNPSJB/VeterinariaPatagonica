while inotifywait -r -q -q -e close_write *;
    do ./manage.py test -v0 --failfast;
    if [ $? -ne 0 ]; 
    then
        play /usr/share/sounds/freedesktop/stereo/bell.oga 2> /dev/null
    else
        play /usr/share/sounds/freedesktop/stereo/complete.oga 2> /dev/null
    fi
done