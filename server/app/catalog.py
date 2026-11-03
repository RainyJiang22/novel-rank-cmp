"""Versioned public-page selections. IDs are source IDs, except named JJ sections.

The catalog declares supported queries, not live source availability.
Fanqie, Jinjiang and Qidian mobile navigation was checked on 2026-11-03.
Only the three retained sources are accepted; removed selections never trigger network access.
"""

from dataclasses import dataclass

from .models import Board, Catalog, Category, Source


def categories(rows, group, boards):
    return tuple(Category(id=str(id_), name=name, group=group, board_ids=boards)
                 for id_, name in rows)


FANQIE_MALE = (
    (1141, "西方奇幻"), (1140, "东方仙侠"), (8, "科幻末世"), (261, "都市日常"),
    (124, "都市修真"), (1014, "都市高武"), (273, "历史古代"), (27, "战神赘婿"),
    (263, "都市种田"), (258, "传统玄幻"), (272, "历史脑洞"), (539, "悬疑脑洞"),
    (262, "都市脑洞"), (257, "玄幻脑洞"), (751, "悬疑灵异"), (504, "抗战谍战"),
    (746, "游戏体育"), (718, "动漫衍生"), (1016, "男频衍生"),
)
FANQIE_FEMALE = (
    (1139, "古风世情"), (8, "科幻末世"), (746, "游戏体育"), (1015, "女频衍生"),
    (248, "玄幻言情"), (23, "种田"), (79, "年代"), (267, "现言脑洞"),
    (246, "宫斗宅斗"), (539, "悬疑脑洞"), (253, "古言脑洞"), (24, "快穿"),
    (749, "青春甜宠"), (745, "星光璀璨"), (747, "女频悬疑"), (750, "职场婚恋"),
    (748, "豪门总裁"), (1017, "民国言情"),
)
JINJIANG_CATEGORIES = (
    ("ancient-romance", "古代言情"), ("modern-romance", "现代言情"),
    ("time-travel", "古代穿越"), ("modern-danmei", "现代都市纯爱"),
    ("fantasy-danmei", "现代幻想纯爱"), ("ancient-danmei", "古代纯爱"),
    ("fan-danmei", "衍生纯爱"), ("modern-fantasy", "幻想现言"),
    ("fantasy-romance", "奇幻言情"), ("future-mystery", "未来游戏悬疑"),
    ("baihe", "百合"), ("no-cp", "无CP"), ("anime-romance", "二次元言情"),
    ("fan-romance", "衍生言情"), ("fan-no-cp", "衍生无cp"),
    ("future-danmei", "未来幻想纯爱"), ("light-novel", "原创轻小说"), ("diverse", "多元"),
)
QIDIAN_CATEGORIES = (
    ("all", "全部分类"), ("21", "玄幻"), ("1", "奇幻"), ("2", "武侠"),
    ("22", "仙侠"), ("4", "都市"), ("15", "现实"), ("6", "军事"),
    ("5", "历史"), ("7", "游戏"), ("8", "体育"), ("9", "科幻"),
    ("10", "悬疑灵异"), ("12", "轻小说"),
)

CATALOG = Catalog(sources=(
    Source(id="qidian", name="起点中文网", home_url="https://m.qidian.com/",
           note="官方移动端分类月票榜与畅销榜；月票保留原单位，畅销数值未公开。",
           categories=categories(QIDIAN_CATEGORIES, "男生", ("yuepiao", "hotsales")),
           boards=(Board(id="yuepiao", name="月票榜", metric_label="月票"),
                   Board(id="hotsales", name="畅销榜", metric_label="销售排名（数值未公开）"))),
    Source(id="fanqie", name="番茄小说", home_url="https://fanqienovel.com/",
           note="原站阅读榜/新书榜；通过公开作品详情补全被字体编码的名称。",
           categories=categories(((f"1_{id_}", name) for id_, name in FANQIE_MALE),
                                 "男频", ("reading", "new")) +
                      categories(((f"0_{id_}", name) for id_, name in FANQIE_FEMALE),
                                 "女频", ("reading", "new")),
           boards=(Board(id="reading", name="阅读榜", metric_label="在读人数"),
                   Board(id="new", name="新书榜", metric_label="在读人数"))),
    Source(id="jinjiang", name="晋江文学城", home_url="https://www.jjwxc.net/",
           note="收入金榜按官方分类分组；只提供顺序，金额未公开，不等同月榜。",
           categories=categories(JINJIANG_CATEGORIES, "收入金榜", ("gold",)),
           boards=(Board(id="gold", name="分类收入金榜", metric_label="收入排名（金额未公开）"),)),
))


@dataclass(frozen=True)
class Selection:
    source: Source
    category: Category
    board: Board

    @property
    def key(self):
        return self.source.id, self.category.id, self.board.id

    @property
    def url(self):
        source, category, board = self.key
        if source == "fanqie":
            gender, genre = category.split("_")
            kind = "2" if board == "reading" else "1"
            return f"https://fanqienovel.com/rank/{gender}_{kind}_{genre}"
        if source == "jinjiang":
            return "https://www.jjwxc.net/topten.php?orderstr=12"
        suffix = "" if category == "all" else f"catid{category}/"
        return f"https://m.qidian.com/rank/{board}/{suffix}"


def validate_selection(source: str, category: str, board: str) -> Selection:
    for site in CATALOG.sources:
        if site.id != source:
            continue
        for genre in site.categories:
            if genre.id == category and board in genre.board_ids:
                return Selection(site, genre, next(b for b in site.boards if b.id == board))
    raise ValueError("网站、分类与榜单组合不受支持，请从 /api/v1/catalog 选择。")
