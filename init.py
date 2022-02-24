import os


def main():
    with open("config.json", "w", encoding="utf-8") as fp:
        fp.write("""{
  "stage": 1,
  "ban_list": [
    
  ],
  "miss_list": [
    
  ]
}""")
    with open("stage_1.xlsx", "w", encoding="utf-8") as fp:
        pass
    with open("stage_2.xlsx", "w", encoding="utf-8") as fp:
        pass
    with open("stage_3.xlsx", "w", encoding="utf-8") as fp:
        pass
    if os.path.exists("temp") is False:
        os.mkdir("temp")
    print("finish")
    return 0


if __name__ == "__main__":
    opt = input("Are you sure you want to reset? \n"
                "Include: config.json, stage_1.xlsx, stage_2.xlsx, stage_3.xlsx \n"
                "(y/n): ")
    if opt == "y" or opt == "yes" or opt == "Y" or opt == "YES":
        exit(main())
    else:
        print("stop")
        exit(0)
