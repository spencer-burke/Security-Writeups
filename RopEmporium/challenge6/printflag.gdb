b *0x40063a
r < input
commands
    printf "current flag\n"
    x/s 0x601028
    continue
end
continue