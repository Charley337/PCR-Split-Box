import json


def main():
    with open("config.json", "w", encoding="utf-8") as fp:
        config = dict()
        config["stage"] = 1
        config["ban_list"] = ["万圣忍", "万圣兔"]
        config["miss_list"] = ["圣克", "圣千", "露娜"]
        json.dump(config, fp, ensure_ascii=False)
    with open("stage_1.xlsx", "w", encoding="utf-8") as fp:
        pass
    with open("stage_2.xlsx", "w", encoding="utf-8") as fp:
        pass
    with open("stage_3.xlsx", "w", encoding="utf-8") as fp:
        pass
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
