import fnmatch
import string
import random
from wordfreq import word_frequency


class WordleSolver:
    def __init__(self) -> None:
        with open("words.txt") as f:
            self.word_list = f.read().splitlines()
        self.glob = [set(string.ascii_lowercase) for _ in range(5)]  # list of sets
        self.include = set()
        self.first_guess = "arose"
        self.solved = False

    def pprint_glob(self):
        """Returns a properly formatted glob for fnmatching / printing"""
        glob = ""
        for g in self.glob:
            if g == set(string.ascii_lowercase):
                glob += "[a-z]"  # for clarity
            else:
                glob += "[" + "".join(sorted(g)) + "]"

        return glob

    def generate_guess(self, guess_num):
        """generate guess word based on current glob"""

        # first run, get random starter from top of list
        if guess_num == 0:
            guess = self.word_list[random.randint(0, 12)]

        # else filter from word list
        else:
            # filter from glob
            self.word_list = fnmatch.filter(self.word_list, self.pprint_glob())

            # filter from includes
            self.word_list = list(
                word
                for word in self.word_list
                if all(letter in word for letter in self.include)
            )

            # Rank remaining words in list
            if self.word_list:
                # sort by descending count of disctinct letters, then descending by frequency of word
                self.word_list.sort(key=lambda word: (len(set(list(word))), word_frequency(word, 'en')), reverse=True)
                guess = self.word_list[0]
            else:
                raise Exception("Word list is empty!")

        return guess

    def get_user_result(self, guess):
        while True:
            try:
                result = input(
                    f"Guessed '{guess}'. What was result? (b=black, y=yellow, g=green, w=win, c=change word): "
                )
            except (EOFError, KeyboardInterrupt):
                print("\n")
                exit("Quitting")

            # user won
            if result == "w":
                return guess, result

            # user changed word entered
            elif result == "c":
                while True:
                    try:
                        new_guess = input("What was alternate word entered?: ")
                    except (EOFError, KeyboardInterrupt):
                        break

                    if len(new_guess) != 5:
                        print("invalid input. Try again.")
                    elif not new_guess.islower():
                        print("invalid input. Try again.")
                    else:
                        guess = new_guess
                        print(f"caputured new guess '{guess}'. Enter result.")
                        break

            # process normal green/black/yellow feedback
            elif len(result) != 5:
                print("invalid input. Try again.")
            elif not set(result) <= set(["b", "g", "y"]):
                print("invalid input. Try again.")
            else:
                return guess, result

    def process_feedback(self, guess):
        # check result of guess
        guess, result = self.get_user_result(guess)

        # user won
        if set(result) == set("g") or result == "w":
            self.solved = True
            return

        # process feeback
        for i, feedbk_ltr in enumerate(result):
            letter = guess[i]
            if feedbk_ltr == "g":
                # set glob letter
                self.glob[i] = letter
            elif feedbk_ltr == "y":
                # letter is present in wordle, but not at this position
                if isinstance(self.glob[i], set):
                    self.glob[i].remove(letter)
                self.include.add(letter)  # include this letter for filtering
            elif feedbk_ltr == "b":
                # letter not present in wordle, remove from all positions if
                # not already in include list (duplicate letter)
                for g in self.glob:
                    if isinstance(g, set) and letter not in self.include:
                        # do not operate if we've already found this letter
                        g.discard(letter)

        print(f"glob = '{self.pprint_glob()}'")
        print(f"must include {sorted(self.include)}")

    def play(self):
        for i in range(6):
            if i == 5:
                print("last guess! :o")

            guess = self.generate_guess(i)
            print(f"{len(self.word_list)} possible words.")
            print(f"Try '{guess}'. Alternate words: {self.word_list[1:6]}")

            self.process_feedback(guess)

            if self.solved:
                print(f"Win in {i + 1} guesses!")
                return

        # loss, too many guesses
        self.generate_guess(i)  # process last feedback
        print(f"Loss :(")
        print(f"{len(self.word_list)} remaining words: {self.word_list[:10]}")


if __name__ == "__main__":
    # repeatably play until quit
    while True:
        w = WordleSolver()
        w.play()

        while True:
            try:
                i = input("Play again? (y/n): ")
                print("\n")
            except (EOFError, KeyboardInterrupt):
                exit("Quitting")

            if i == "y":
                break
            else:
                exit("Quitting")
