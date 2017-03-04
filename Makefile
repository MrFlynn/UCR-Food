install:
    @echo "--> Installing Dependencies"
    python3 -m pip install -r requirements.txt
    @echo ""

.PHONY install