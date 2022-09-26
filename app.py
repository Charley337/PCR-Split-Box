import pcrhelper as ph
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as msgbox
import threading
import winsound


if __name__ != "__main__":
    exit(0)


# TODO: 数据处理工具
data_handler = ph.DataHandler()
homeworks = None
plans = None
stage = 0
old_mode = ""
data_state = False
# TODO: 信号量
lock_request = threading.Semaphore(1)
lock_search = threading.Semaphore(1)
# TODO: 基本gui配置
gui = tk.Tk()
button_frame = tk.Frame(gui)
button_request = tk.Button(button_frame, text="获取数据")
label_data_state = tk.Label(button_frame, text="未获取数据")
search_frame = tk.Frame(gui)
button_search = tk.Button(search_frame, text="搜索分刀方案")
combo_stage = ttk.Combobox(
    search_frame, state="readonly", width=11,
    values=["请选择 - 阶段", "A 面", "B 面", "C 面", "D 面"]
)
combo_king1 = ttk.Combobox(
    search_frame, state="readonly", width=17,
    values=["请选择 - 第一个BOSS", "一 王", "二 王", "三 王", "四 王", "五 王"]
)
combo_king2 = ttk.Combobox(
    search_frame, state="readonly", width=17,
    values=["请选择 - 第二个BOSS", "一 王", "二 王", "三 王", "四 王", "五 王"]
)
combo_king3 = ttk.Combobox(
    search_frame, state="readonly", width=17,
    values=["请选择 - 第三个BOSS", "一 王", "二 王", "三 王", "四 王", "五 王"]
)
combo_mode = ttk.Combobox(
    search_frame, state="readonly", width=11,
    values=["请选择 - 模式", "auto", "normal"]
)
label_used = tk.Label(gui, text="请输入已经出过的刀的编号(用空格隔开)")
entry_used = tk.Entry(gui, width=50)
msg_box = tk.Text(gui, width=9999, height=9999, undo=True, wrap="char")
scroll = tk.Scrollbar()


# TODO: 一般函数
def msg_box_rewrite(message: str):
    msg_box.config(state=tk.NORMAL)
    msg_box.delete(0.0, tk.END)
    msg_box.insert(tk.INSERT, message)
    msg_box.config(state=tk.DISABLED)


def msg_box_insert(message: str):
    msg_box.config(state=tk.NORMAL)
    msg_box.insert(tk.INSERT, message)
    msg_box.config(state=tk.DISABLED)


def homeworks_init():
    """homeworks初始化，只读取本地文件，不会发起request，若没有本地文件则放弃"""
    global homeworks
    global data_state
    homeworks = data_handler.get_hws_from_data_files(mode="never")
    if homeworks is not None:
        data_state = True


def gui_settings():
    """配置gui界面"""
    # gui界面
    gui.title("公会战排刀工具")
    gui.geometry("1200x800+370+90")
    gui.resizable(False, False)
    # 按钮frame
    button_frame.pack(padx=10, pady=10)
    # 获取数据的按钮
    button_request.pack(padx=10, pady=10, side=tk.LEFT)
    # 显示是否获取了数据
    label_data_state.pack(padx=10, pady=10, side=tk.LEFT)
    if data_state:
        label_data_state.config(text="已获取数据", fg="green")
    else:
        label_data_state.config(fg="red")
    # 搜索分刀frame
    search_frame.pack(padx=10, pady=10)
    # 搜索分刀按钮
    button_search.pack(padx=10, pady=10, side=tk.LEFT)
    # 选择模式组合框
    combo_mode.current(1)
    combo_mode.pack(padx=10, pady=10, side=tk.LEFT)
    # 会战阶段组合框
    combo_stage.current(0)
    combo_stage.pack(padx=10, pady=10, side=tk.LEFT)
    # 选择第一个BOSS组合框
    combo_king1.current(0)
    combo_king1.pack(padx=10, pady=10, side=tk.LEFT)
    # 选择第二个BOSS组合框
    combo_king2.current(0)
    combo_king2.pack(padx=10, pady=10, side=tk.LEFT)
    # 选择第三个BOSS组合框
    combo_king3.current(0)
    combo_king3.pack(padx=10, pady=10, side=tk.LEFT)
    # 已经出过的刀
    label_used.pack(padx=10, pady=0)
    entry_used.pack(padx=10, pady=0)
    # 文本框滚动条
    scroll.config(command=msg_box.yview)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)
    # 文本框 - 显示结果
    msg_box.config(yscrollcommand=scroll.set)
    msg_box_rewrite("Welcome!")
    msg_box.pack(padx=10, pady=20)


def search_plans(boss1: str, boss2: str, boss3: str, used: list):
    """从所有分刀方案中，搜索需要的boss组合，默认显示前20条，剩余部分保存至 search.txt 中"""
    global plans
    if plans is None:
        msg_box_rewrite("没有找到分刀方案")
        return
    if not isinstance(used, list):
        used = []
    boss = [str(boss1), str(boss2), str(boss3)]
    boss.sort()
    msg_box_rewrite("")
    cnt = 0
    for plan in plans:
        if boss == [ph.sn2king(plan.h1.sn)[1], ph.sn2king(plan.h2.sn)[1], ph.sn2king(plan.h3.sn)[1]]:
            flag = True
            for u in used:
                flag = flag and (u in plan.sn)
                if flag is False:
                    break
            if flag:
                plan_txt = "number: {}\ndamage: {}\nscore: {}\n[{}]\nborrow: {}\n{}\nh1:\n{}\nh2:\n{}\nh3:\n{}\n\n\n".format(
                    cnt + 1, plan.damage, plan.score, plan.sn, plan.borrow, plan.names, plan.h1.video, plan.h2.video, plan.h3.video
                )
                if cnt < 30:
                    msg_box_insert(plan_txt)
                else:
                    break
                cnt += 1


# TODO: 以下部分是事件响应函数
def onclick_button_search(event):

    def thread_target(stage_now, mode):
        global stage
        global plans
        global old_mode
        if mode not in ["normal", "auto"]:
            raise ValueError('mode can not be "{}"'.format(mode))
        temp_stage_list = ["none", "A", "B", "C", "D"]
        if stage != stage_now or old_mode != mode:
            stage = stage_now
            old_mode = mode
            if mode == "auto":
                plans = homeworks.get_plans_auto(stage=temp_stage_list[temp_stage], sort_key="score", reverse=True)
            elif mode == "normal":
                plans = homeworks.get_plans(stage=temp_stage_list[temp_stage], sort_key="score", reverse=True)
            else:
                raise Exception("unknown error!")
        search_plans(str(temp_king1), str(temp_king2), str(temp_king3), temp_used)
        lock_search.release()

    if not lock_search.acquire(blocking=False):
        winsound.MessageBeep()
        return
    if not data_state or homeworks is None:
        msg_box_rewrite("需要先获取数据")
        winsound.MessageBeep()
        lock_search.release()
        return
    temp_stage = combo_stage.current()
    temp_king1 = combo_king1.current()
    temp_king2 = combo_king2.current()
    temp_king3 = combo_king3.current()
    temp_mode = combo_mode.current()
    temp_used = entry_used.get()
    temp_used = temp_used.split(" ")
    if temp_stage * temp_king1 * temp_king2 * temp_king3 * temp_mode == 0:
        msg_box_rewrite("信息不完整")
        winsound.MessageBeep()
        lock_search.release()
        return
    msg_box_rewrite("正在搜索中，请稍后...")
    temp_mode_list = ["none", "auto", "normal"]
    thread = threading.Thread(target=thread_target, args=(temp_stage, temp_mode_list[temp_mode]))
    thread.start()


def onclick_button_request(event):
    global plans

    def thread_target():
        global homeworks
        global data_state
        try:
            homeworks = data_handler.get_hws_from_data_files(mode="always")
            data_state = True
            msgbox.showinfo(title="成功", message="成功获取数据")
            msg_box_rewrite("获取成功")
            label_data_state.config(text="已获取数据", fg="green")
        except:
            homeworks = None
            data_state = False
            msgbox.showerror(title="错误", message="网络错误! (可能要爬个梯子)")
            label_data_state.config(text="未获取数据", fg="red")
            msg_box_rewrite("获取失败，可能需要爬个梯子")
        lock_request.release()

    if not lock_request.acquire(blocking=False):
        winsound.MessageBeep()
    else:
        msg_box_rewrite("开始获取数据，请稍等...")
        label_data_state.config(text="正在获取中", fg="blue")
        thread = threading.Thread(target=thread_target)
        thread.start()


def button_bind():
    """按钮绑定点击事件函数"""
    button_request.bind("<Button-1>", onclick_button_request)
    button_search.bind("<Button-1>", onclick_button_search)


# TODO: gui主要设置流程
def app_settings():
    """main函数 - 主要构建整个gui实现逻辑"""
    homeworks_init()
    gui_settings()
    button_bind()


# TODO: 程序开始运行
app_settings()
gui.mainloop()
