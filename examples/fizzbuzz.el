SEEK GRACE
INSCRIBE counter 1

ERDTREE LOOP
    FOG GATE counter EXCEEDS 100
        FELL THE TREE
    LIFT FOG
    INSCRIBE mod_count counter
    MODULO mod_count 15
    FOG GATE mod_count IS 0 ~ divisible by 3 and 5
        ECHO "FizzBuzz"
    MIST
        FOG GATE mod_count IS 3
            ECHO "Fizz"
        MIST
            FOG GATE mod_count IS 5
                ECHO "Buzz"
            MIST
                FOG GATE mod_count IS 6
                    ECHO "Fizz"
                MIST
                    FOG GATE mod_count IS 9
                        ECHO "Fizz"
                    MIST
                        FOG GATE mod_count IS 10
                            ECHO "Buzz"
                        MIST
                            FOG GATE mod_count IS 12
                                ECHO "Fizz"
                            MIST
                                ECHO counter
                            LIFT FOG
                        LIFT FOG
                    LIFT FOG
                LIFT FOG
            LIFT FOG
        LIFT FOG
    LIFT FOG

    KINDLE counter 1
ROOTS END
OFFER REMEMBRANCE