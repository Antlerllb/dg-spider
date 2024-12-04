# encoding: utf-8
import hashlib
import time
from datetime import datetime, timedelta
import scrapy
import re


class OldFormatUtil():
    @staticmethod
    def remove_invalid_utf8(text):
        utf8_pattern = re.compile('[\x00-\x7F\u4e00-\u9fff]+')  # ASCII和中文
        clean_text = utf8_pattern.findall(text)
        cleaned_text = ''.join(clean_text)
        return cleaned_text

    @staticmethod
    def remove_errno22_lines_in_file(file_path):
        """
        处理日志文件中多余的 Errno 22 报错行，提高日志的可读性和错误排查效率。
        Parameters:
            file_path (str): 日志文件的完整路径。
        Note:
            - 该方法适用于日志文件，其中 Errno 22 行通常是与文件或路径访问相关的异常信息。
            - 通过处理多余的 Errno 22 行，可以提高日志的可读性和错误排查效率。
        """
        with open(file_path, 'r', encoding='utf-8') as file:  # 读取文件内容
            lines = file.readlines()
        output_lines = []  # 根据条件删除满足条件的行
        skip_lines = 0
        for i, line in enumerate(lines):
            if skip_lines > 0:
                skip_lines -= 1
                continue
            if re.search(r'Errno 22', line):  # 找到下一个包含 'ERROR', 'WARNING', or 'INFO' 的行
                next_line_index = i + 1
                while next_line_index < len(lines):
                    if re.search(r'ERROR|WARNING|INFO', lines[next_line_index]):
                        break
                    next_line_index += 1
                skip_lines = next_line_index - i  # 跳过errno行，直到下一条日志
            else:
                output_lines.append(line)
        with open(file_path, 'w', encoding='utf-8') as file:  # # 将修改后的内容写回文件
            file.writelines(output_lines)

    @staticmethod
    def format_time(time_):
        if not time_:
            return None
        if time_.isdigit():
            return int(time_)
        if time_ == 'now':
            return int(time.time())
        days = re.findall(r'days_ago:(\d+)', time_)
        if days:
            return OldDateUtil.get_time_ago_stamp(day=int(days[0]))

    @staticmethod
    def extract_email(text_):
        match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', text_)
        if match:
            return match.group()
        else:
            return None

    @staticmethod
    def url_md5(url):
        m = hashlib.md5()
        m.update(url.encode(encoding='utf-8'))
        return m.hexdigest()


class OldDateUtil():
    MOZILLA_HEADER = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

    @staticmethod
    def get_now_datetime_str() -> str:
        """
        返回当前的格式化时间，格式：%Y-%m-%d %H:%M:%S
        """
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    @staticmethod
    def str_datetime_to_timestamp(time_: str) -> int:
        """
        将传入的格式化时间转为时间戳，格式：%Y-%m-%d %H:%M:%S
        """
        return int(time.mktime(time.strptime(time_, "%Y-%m-%d %H:%M:%S")))

    @staticmethod
    def timestamp_to_datetime_str(time_):
        """
        将传入的时间戳转为格式化时间，格式：%Y-%m-%d %H:%M:%S
        """
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time_)))

    @staticmethod
    def get_time_ago_stamp(year=0, month=0, week=0, day=0, hour=0, minute=0, second=0):
        """
        返回指定时间之前的时间戳
        """
        stamp = int(
            time.time()) - second - minute * 60 - hour * 3600 - day * 86400 - week * 604800 - month * 2592000 - year * 31536000
        return stamp if stamp > 0 else 0

    @staticmethod
    def get_day_ago_datetime_str(day=0):
        """
        获取 n天前 零点的 datetime
        """
        current_datetime = datetime.now()
        day_ago = current_datetime - timedelta(days=day)
        day_ago_midnight = day_ago.replace(hour=0, minute=0, second=0, microsecond=0)   # 转换为0点
        datetime_str = day_ago_midnight.strftime('%Y-%m-%d %H:%M:%S')
        return datetime_str

    @staticmethod
    def format_time_english(data1):
        """
        格式化各类网站时间字符串，格式：%Y-%m-%d %H:%M:%S
        """
        data = ''
        list = [i for i in re.split('/| |,|:|\n|\r|\f|\t|\v', data1) if i != '']
        for i in list:
            data += (i + ' ')
        data = data.strip()
        if re.findall(r'\S+ \d+ \d+ \d+ \d+', data) != []:
            num = 0
            while list[num] not in OldDateUtil.EN_1866_DATE.keys():
                num += 1
            return time.strftime("%Y-%m-%d %H:%M:%S",
                                 datetime(int(list[num + 2]), OldDateUtil.EN_1866_DATE[list[num]], int(list[num + 1]),
                                          int(list[num + 3]), int(list[num + 4])).timetuple())
        elif re.findall(r'\S+ \d+ \d+', data) != []:
            num = 0
            while list[num] not in OldDateUtil.EN_1866_DATE.keys():
                num += 1
            return time.strftime("%Y-%m-%d %H:%M:%S",
                                 datetime(int(list[num + 2]), OldDateUtil.EN_1866_DATE[list[num]], int(list[num + 1])).timetuple())
        elif re.findall(r'\d+ hours ago', data) != [] or re.findall(r'\d+ hour ago', data) != []:
            num = 0
            while re.findall(r'\d+', list[num]) == []:
                num += 1
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - int(list[num]) * 3600))
        elif re.findall(r'\d+ days ago', data) != [] or re.findall(r'\d+ day ago', data) != []:
            num = 0
            while re.findall(r'\d+', list[num]) == []:
                num += 1
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - int(list[num]) * 86400))
        elif re.findall(r'\d+ weeks ago', data) != [] or re.findall(r'\d+ week ago', data) != []:
            num = 0
            while re.findall(r'\d+', list[num]) == []:
                num += 1
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - int(list[num]) * 604800))
        elif re.findall(r'\d+ months ago', data) != [] or re.findall(r'\d+ month ago', data) != []:
            num = 0
            while re.findall(r'\d+', list[num]) == []:
                num += 1
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - int(list[num]) * 2592000))
        elif re.findall(r'\d+ years ago', data) != [] or re.findall(r'\d+ year ago', data) != []:
            num = 0
            while re.findall(r'\d+', list[num]) == []:
                num += 1
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - int(list[num]) * 31536000))
        else:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    

    def format_time(t=0):
        if t == 0:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        else:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))

    @staticmethod
    def format_time2(data1):
        data = ''
        list = [i for i in re.split('/| |,|:|\n|\r|\f|\t|\v',data1) if i!='']
        for i in list:
            data += (i+' ')
        data = data.strip()
        if re.findall(r'\S+ \d+ \d+ \d+ \d+',data) != []:
            num = 0
            while list[num] not in  OldDateUtil.month.keys():
                num += 1
            return time.strftime("%Y-%m-%d %H:%M:%S", datetime(int(list[num+2]), OldDateUtil.month[list[num]],int(list[num+1]),int(list[num+3]),int(list[num+4])).timetuple())
        elif re.findall(r'\S+ \d+ \d+',data) != []:
            num = 0
            while list[num] not in  OldDateUtil.month.keys():
                num += 1
            return time.strftime("%Y-%m-%d %H:%M:%S", datetime(int(list[num+2]), OldDateUtil.month[list[num]],int(list[num+1])).timetuple())
        elif re.findall(r'\d+ hours ago',data) != [] or re.findall(r'\d+ hour ago',data) != []:
            num = 0
            while re.findall(r'\d+',list[num])==[]:
                num += 1
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()-int(list[num])*3600))
        elif re.findall(r'\d+ days ago',data) != [] or re.findall(r'\d+ day ago',data) != []:
            num = 0
            while re.findall(r'\d+',list[num])==[]:
                num += 1
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()-int(list[num])*86400))
        elif re.findall(r'\d+ weeks ago',data) != [] or re.findall(r'\d+ week ago',data) != []:
            num = 0
            while re.findall(r'\d+',list[num])==[]:
                num += 1
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()-int(list[num])*604800))
        elif re.findall(r'\d+ months ago',data) != [] or re.findall(r'\d+ month ago',data) != []:
            num = 0
            while re.findall(r'\d+',list[num])==[]:
                num += 1
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()-int(list[num])*2592000))
        elif re.findall(r'\d+ years ago',data) != [] or re.findall(r'\d+ year ago',data) != []:
            num = 0
            while re.findall(r'\d+',list[num])==[]:
                num += 1
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()-int(list[num])*31536000))
        else:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

    @staticmethod
    def format_time3(data):
        timeArray = time.strptime(data, "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray))
        return timeStamp

    time = None

    BN_1779_DATE = {
        'জানুয়ারি': 1,
        'ফেব্রুয়ারি': 2,
        'মার্চ': 3,
        'এপ্রিল': 4,
        'মে': 5,
        'জুন': 6,
        'জুলাই': 7,
        'আগস্ট': 8,
        'সেপ্টেম্বর': 9,
        'অক্টোবর': 10,
        'নভেম্বর': 11,
        'ডিসেম্বর': 12,
        '০': 0,
        '১': 1,
        '২': 2,
        '৩': 3,
        '৪': 4,
        '৫': 5,
        '৬': 6,
        '৭': 7,
        '৮': 8,
        '৯': 9,
    }

    AF_1735_DATE = {
        'Januarie': 1,
        'Februarie': 2,
        'Maart': 3,
        'April': 4,
        'Mei': 5,
        'Junie': 6,
        'Julie': 7,
        'Augustus': 8,
        'September': 9,
        'Oktober': 10,
        'November': 11,
        'Desember': 12,
    }

    SQ_1739_DATE = {
        'Janar': 1,
        'Shkurt': 2,
        'Mars': 3,
        'Prill': 4,
        'Maj': 5,
        'Qershor': 6,
        'Korrik': 7,
        'Gusht': 8,
        'Shtator': 9,
        'Tetor': 10,
        'Nëntor': 11,
        'Dhjetor': 12,
    }

    AM_1744_DATE = {
        'ጃንዋሪ (ጥር)': 1,
        'ፌብሩዋሪ አይደለም መኖርያችን': 2,
        'ማርች': 3,
        'ኤፕሪል': 4,
        'ሜይ': 5,
        'ጁን': 6,
        'ጁላይ': 7,
        'ኦገስት': 8,
        'ሴፕቴምበር': 9,
        'ኦክቶበር': 10,
        'ኖቬምበር': 11,
        'ዲሴምበር': 12,
    }

    AR_1748_DATE = {
        'يناير': 1,
        'فبراير': 2,
        'مارس': 3,
        'إبريل': 4,
        'مايو': 5,
        'يونيو': 6,
        'جويلية': 7,
        'أغسطس': 8,
        'سبتمبر': 9,
        'أكتوبر': 10,
        'نوفمبر': 11,
        'ديسمبر': 12,
    }

    HY_1751_DATE = {
        'Հունվար': 1,
        'Փետրվար': 2,
        'Մարտ': 3,
        'Ապրիլ': 4,
        'Մայիս': 5,
        'Հունիս': 6,
        'Հուլիս': 7,
        'Օգոստոս': 8,
        'Սեպտեմբեր': 9,
        'Հոկտեմբեր': 10,
        'Նոյեմբեր': 11,
        'Դեկտեմբեր': 12,
    }

    AS_1757_DATE = {
        'জানুৱাৰী': 1,
        'ফেব্ৰুৱাৰী': 2,
        'মাৰ্চ': 3,
        'এপ্ৰিল': 4,
        'মে': 5,
        'জুন': 6,
        'জুলাই': 7,
        'আগষ্ট': 8,
        'ছেপ্টেম্বৰ': 9,
        'অক্টোবৰ': 10,
        'নৱেম্বৰ': 11,
        'ডিচেম্বৰ': 12,
    }

    AZ_1765_DATE = {
        'Yanvar': 1,
        'Fevral': 2,
        'Mart': 3,
        'Aprel': 4,
        'May': 5,
        'İyun': 6,
        'İyul': 7,
        'Avqust': 8,
        'Sentyabr': 9,
        'Oktyabr': 10,
        'Noyabr': 11,
        'Dekabr': 12,
    }

    BA_1768_DATE = {
        'Ғинуар': 1,
        'Февраль': 2,
        'Март': 3,
        'Апрель': 4,
        'Май': 5,
        'Июнь': 6,
        'Июль': 7,
        'Август': 8,
        'Сентябрь': 9,
        'Октябрь': 10,
        'Ноябрь': 11,
        'Декабрь': 12,
    }

    EU_1772_DATE = {
        'Urtarrila': 1,
        'Otsaila': 2,
        'Martxoa': 3,
        'Apirila': 4,
        'Maiatza': 5,
        'Ekaina': 6,
        'Uztaila': 7,
        'Abuztua': 8,
        'Iraila': 9,
        'Urria': 10,
        'Azaroa': 11,
        'Abendua': 12,
    }

    BE_1777_DATE = {
        'Студзень': 1,
        'Люты': 2,
        'Сакавік': 3,
        'Красавік': 4,
        'Май': 5,
        'Чэрвень': 6,
        'Ліпень': 7,
        'Жнівень': 8,
        'Верасень': 9,
        'Кастрычнік': 10,
        'Лістапад': 11,
        'Снежань': 12,
    }

    BO_1788_DATE = {
        'ཟླ་དང་པོ།': 1,
        'ཟླ་2པར།': 2,
        'ཟླ་བ་གསུམ་པ།': 3,
        'ཟླ་4པར།': 4,
        'ཟླ་བ་ལྔ་པ': 5,
        'ཟླ་6པར།': 6,
        'ཟླ་7པ།': 7,
        'ཟླ་བརྒྱད་པ།': 8,
        'ཟླ་9པ།': 9,
        'ཟླ་བ་བཅུ་པ།': 10,
        'ཟླ་11པར།': 11,
        'ཟླ་བ་བཅུ་གཉིས་': 12,
    }

    BS_1790_DATE = {
        'Januar': 1,
        'Februar': 2,
        'Mart': 3,
        'April': 4,
        'Maj': 5,
        'Jun': 6,
        'Juli': 7,
        'August': 8,
        'Septembar': 9,
        'Oktobar': 10,
        'Novembar': 11,
        'Decembar': 12,
    }

    BR_1792_DATE = {
        'Genver': 1,
        'C’hwevrer': 2,
        'Meurzh': 3,
        'Ebrel': 4,
        'Mae': 5,
        'Mezheven': 6,
        'Gouere': 7,
        'Eost': 8,
        'Gwengolo': 9,
        'Here': 10,
        'Du': 11,
        'Kerzu': 12,
    }

    BG_1796_DATE = {
        'Януари': 1,
        'Февруари': 2,
        'Март': 3,
        'Април': 4,
        'Май': 5,
        'Юни': 6,
        'юли': 7,
        'Август': 8,
        'Сeптември': 9,
        'Октомври': 10,
        'Ноември': 11,
        'Декември': 12,
    }

    MY_1797_DATE = {
        'ဇန်နဝါရီလ': 1,
        'ဖေဖော်ဝါရီ': 2,
        'မတ်လ': 3,
        'ဧပြီလ': 4,
        'မေလ': 5,
        'ဇွန်လ': 6,
        'ဇူလိုင်လ': 7,
        'ဩဂုတ္': 8,
        'စက်တင်ဘာလ': 9,
        'ေအာက္တိုဘာ': 10,
        'နိုဝင္ဘာ': 11,
        'ဒီဇင်ဘာ': 12,
    }

    CA_1803_DATE = {
        'Gener': 1,
        'Febrer': 2,
        'Març': 3,
        'Abril': 4,
        'Maig': 5,
        'Juny': 6,
        'Juliol': 7,
        'Agost': 8,
        'Septembre': 9,
        'Octubre': 10,
        'Novembre': 11,
        'Desembre': 12,
    }

    CS_1807_DATE = {
        'Leden': 1,
        'Únor': 2,
        'Březen': 3,
        'Duben': 4,
        'Květen': 5,
        'Červen': 6,
        'Červenec': 7,
        'Srpen': 8,
        'Září': 9,
        'Říjen': 10,
        'Listopad': 11,
        'Prosinec': 12,
    }

    CY_1836_DATE = {
        'Ionawr': 1,
        'Chwefror': 2,
        'Mawrth': 3,
        'Ebrill': 4,
        'Mai': 5,
        'Mehefin': 6,
        'Gorffennaf': 7,
        'Awst': 8,
        'Medi': 9,
        'Hydref': 10,
        'Tachwedd': 11,
        'Rhagfyr': 12,
    }

    CS_1838_DATE = {
        'Leden': 1,
        'Únor': 2,
        'Březen': 3,
        'Duben': 4,
        'Květen': 5,
        'Červen': 6,
        'Červenec': 7,
        'Srpen': 8,
        'Září': 9,
        'Říjen': 10,
        'Listopad': 11,
        'Prosinec': 12,
    }

    DA_1841_DATE = {
        'Januar': 1,
        'Februar': 2,
        'Marts': 3,
        'April': 4,
        'Maj': 5,
        'Juni': 6,
        'Juli': 7,
        'August': 8,
        'September': 9,
        'Oktober': 10,
        'November': 11,
        'December': 12,
    }

    DE_1846_DATE = {
        'January': 1,
        'Februar': 2,
        'März': 3,
        'April': 4,
        'Mai': 5,
        'June': 6,
        'Juli': 7,
        'August': 8,
        'September': 9,
        'Oktober': 10,
        'November': 11,
        'Dezember': 12,
    }

    DV_1850_DATE = {
        'ޖެނުއަރީ': 1,
        'ފެބްރުއަރީ': 2,
        'މާރޗް': 3,
        'އެޕްރީލް': 4,
        'މެއި': 5,
        'ޖޫން': 6,
        'ޖުލައި': 7,
        'އޮގަސްޓު': 8,
        'ސެޕްޓެމްބަރު': 9,
        'އޮކްޓޫބަރު': 10,
        'ނޮވެމްބަރު': 11,
        'ޑިސެމްބަރު': 12,
    }

    NL_1856_DATE = {
        'Januari': 1,
        'februari': 2,
        'maart': 3,
        'april': 4,
        'mei': 5,
        'juni': 6,
        'juli': 7,
        'augustus': 8,
        'September': 9,
        'Oktober': 10,
        'november': 11,
        'december': 12,
    }

    EL_1863_DATE = {
        'Ιανουάριος': 1,
        'Φεβρουάριος': 2,
        'Μάρτιος': 3,
        'Απρίλιος': 4,
        'Μάιος': 5,
        'Ιούνιος': 6,
        'Ιούλιος': 7,
        'Άυγουστος': 8,
        'Σεπτέμβριος': 9,
        'Οκτώβριος': 10,
        'Νοέμβριος': 11,
        'Δεκέμβριος': 12,
    }

    EN_1866_DATE = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12,
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'Jun': 6,
        'Jul': 7,
        'Aug': 8,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12,
    }

    EO_1868_DATE = {
        'January': 1,
        'Februaro': 2,
        'Marto': 3,
        'Aprilo': 4,
        'Majo': 5,
        'Junio': 6,
        'Julio': 7,
        'Aŭgusto': 8,
        'Septembro': 9,
        'Oktobro': 10,
        'Novembro': 11,
        'Decembro': 12,
    }

    ET_1869_DATE = {
        'jaanuar': 1,
        'Veebruar': 2,
        'maarts': 3,
        'aprill': 4,
        'mai': 5,
        'juuni': 6,
        'juuli': 7,
        'august': 8,
        'september': 9,
        'oktoober': 10,
        'November': 11,
        'Detsember': 12,
    }

    EU_1870_DATE = {
        'Urtarrila': 1,
        'Otsaila': 2,
        'Martxoa': 3,
        'Apirila': 4,
        'Maiatza': 5,
        'Ekaina': 6,
        'Uztaila': 7,
        'Abuztua': 8,
        'Iraila': 9,
        'Urria': 10,
        'Azaroa': 11,
        'Abendua': 12,
    }

    FO_1875_DATE = {
        'Januar': 1,
        'Februar': 2,
        'Mars': 3,
        'Apríl': 4,
        'Mai': 5,
        'Juni': 6,
        'Juli': 7,
        'August': 8,
        'September': 9,
        'Oktober': 10,
        'November': 11,
        'Desember': 12,
    }

    FA_1876_DATE = {
        'ژانویه': 1,
        'اردیبهشت': 2,
        'خرداد': 3,
        'تیر': 4,
        'مرداد': 5,
        'شهریور': 6,
        'مهر': 7,
        'آبان': 8,
        'آذر': 9,
        'دی': 10,
        'بهمن': 11,
        'دسامبر': 12,
        '۰': 0,
        '۱': 1,
        '۲': 2,
        '۳': 3,
        '۴': 4,
        '۵': 5,
        '۶': 6,
        '۷': 7,
        '۸': 8,
        '۹': 9,
    }

    FJ_1879_DATE = {
        'Janueri': 1,
        'Veverueri': 2,
        'Maji': 3,
        'Evereli': 4,
        'Me': 5,
        'Jiune': 6,
        'Jiulai': 7,
        'Okosita': 8,
        'Seviteba': 9,
        'Okotova': 10,
        'Noveba': 11,
        'Tiseba': 12,
    }

    FI_1881_DATE = {
        'Tammikuu': 1,
        'Helmikuu': 2,
        'Maaliskuu': 3,
        'Huhtikuu': 4,
        'Toukokuu': 5,
        'Kesäkuu': 6,
        'Heinäkuu': 7,
        'Elokuu': 8,
        'Syyskuu': 9,
        'Lokakuu': 10,
        'Marraskuu': 11,
        'Joulukuu': 12,
    }

    FR_1884_DATE = {
        'Janvier': 1,
        'Février': 2,
        'Mars': 3,
        'Avril': 4,
        'Mai': 5,
        'Juin': 6,
        'Juillet': 7,
        'Août': 8,
        'Septembre': 9,
        'Octobre': 10,
        'novembre': 11,
        'Décembre': 12,
    }

    FRM_1899_DATE = {
        'იანვარი': 1,
        'თებერვალი': 2,
        'მარტი': 3,
        'აპრილი': 4,
        'მაისი': 5,
        'ივნისი': 6,
        'ივლისი': 7,
        'აგვისტო': 8,
        'სექტემბერი': 9,
        'ოქტომბერი': 10,
        'ნოემბერი': 11,
        'დეკემბერი': 12,
    }

    DE_1901_DATE = {
        'January': 1,
        'Februar': 2,
        'März': 3,
        'April': 4,
        'Mai': 5,
        'June': 6,
        'Juli': 7,
        'August': 8,
        'September': 9,
        'Oktober': 10,
        'November': 11,
        'Dezember': 12,
    }

    GD_1905_DATE = {
        'Am Faoilleach': 1,
        'An Gearran': 2,
        'Am Màrt': 3,
        'An Giblean': 4,
        'An Cèitean': 5,
        'An t-Ògmhios': 6,
        'An t-Iuchar': 7,
        'An Lùnastal': 8,
        'An t-Sultain': 9,
        'An Dàmhair': 10,
        'An t-Samhain': 11,
        'An Dùbhlachd': 12,
    }

    GA_1906_DATE = {
        'Eanáir': 1,
        'Feabhra': 2,
        'Márta': 3,
        'Aibreán': 4,
        'Bealtaine': 5,
        'Meitheamh': 6,
        'Iúil': 7,
        'Lúnasa': 8,
        'Meán Fómhair': 9,
        'Deireadh Fómhair': 10,
        'Samhain': 11,
        'Nollaig': 12,
    }

    GL_1907_DATE = {
        'Xaneiro': 1,
        'Febreiro': 2,
        'Marzo': 3,
        'Abril': 4,
        'Maio': 5,
        'Xuño': 6,
        'Xullo': 7,
        'Agosto': 8,
        'Setembro': 9,
        'Outubro': 10,
        'Novembro': 11,
        'Decembro': 12,
    }

    EL_1916_DATE = {
        'Ιανουάριος': 1,
        'Φεβρουάριος': 2,
        'Μάρτιος': 3,
        'Απρίλιος': 4,
        'Μάιος': 5,
        'Ιούνιος': 6,
        'Ιούλιος': 7,
        'Άυγουστος': 8,
        'Σεπτέμβριος': 9,
        'Οκτώβριος': 10,
        'Νοέμβριος': 11,
        'Δεκέμβριος': 12,
    }

    GU_1920_DATE = {
        'જાન્યુઆરી': 1,
        'ફેબ્રુઆરીMarch long': 2,
        'માર્ચ': 3,
        'એપ્રિલMay long': 4,
        'મે': 5,
        'જૂન': 6,
        'જૂલાઈAugust long': 7,
        'ઓગસ્ટ': 8,
        'સપ્ટેમ્બર': 9,
        'ઓક્ટોબર': 10,
        'નવેમ્બર': 11,
        'ડિસેમ્બરMonday': 12,
    }

    HT_1923_DATE = {
        'Janvye': 1,
        'Fevriye': 2,
        'Mas': 3,
        'Avril': 4,
        'Me': 5,
        'Jwen': 6,
        'Jiyè': 7,
        'Out': 8,
        'Septanm': 9,
        'Oktòb': 10,
        'Novanm': 11,
        'Desanm': 12,
    }

    HE_1926_DATE = {
        'ינואר': 1,
        'פברואר': 2,
        'מרץ': 3,
        'אפריל': 4,
        'מאי': 5,
        'יוני': 6,
        'יולי': 7,
        'אוגוסט': 8,
        'ספטמבר': 9,
        'אוקטובר': 10,
        'נובמבר': 11,
        'דצמבר': 12,
    }

    HI_1930_DATE = {
        'जनवरी': 1,
        'फरवरी': 2,
        'मार्च': 3,
        'अप्रैल': 4,
        'मई': 5,
        'जून': 6,
        'जुलाई': 7,
        'अगस्त': 8,
        'सितम्बर': 9,
        'अक्टूबर': 10,
        'नवम्बर': 11,
        'दिसंबर': 12,
    }

    HR_1934_DATE = {
        'Siječanj': 1,
        'Veljača': 2,
        'Ožujak': 3,
        'Travanj': 4,
        'svibanj': 5,
        'Lipanj': 6,
        'Srpanj': 7,
        'Kolovoz': 8,
        'Rujan': 9,
        'Listopad': 10,
        'Studeni': 11,
        'Prosinac': 12,
    }

    HU_1936_DATE = {
        'Január': 1,
        'Február': 2,
        'Március': 3,
        'Április': 4,
        'Május': 5,
        'Június': 6,
        'Július': 7,
        'Augusztus': 8,
        'Szeptember': 9,
        'Október': 10,
        'November': 11,
        'December': 12,
    }

    HY_1938_DATE = {
        'Հունվար': 1,
        'Փետրվար': 2,
        'Մարտ': 3,
        'Ապրիլ': 4,
        'Մայիս': 5,
        'Հունիս': 6,
        'Հուլիս': 7,
        'Օգոստոս': 8,
        'Սեպտեմբեր': 9,
        'Հոկտեմբեր': 10,
        'Նոյեմբեր': 11,
        'Դեկտեմբեր': 12,
    }

    IS_1942_DATE = {
        'janúar': 1,
        'febrúar': 2,
        'mars': 3,
        'apríl': 4,
        'maí': 5,
        'júní': 6,
        'júlí': 7,
        'ágúst': 8,
        'september': 9,
        'október': 10,
        'nóvember': 11,
        'desember': 12,
    }

    IU_1947_DATE = {
        'ᔭᓄᐊᕆ/ᓇᓕᕐᙯᑐᖅ': 1,
        'ᕕᐳᐊᕆ/ᐊᕗᓐᓂᑎ': 2,
        'ᒫᑦᓯ/ᓇᑦᓯᐊᓕᐅᑦ': 3,
        'ᐁᕆᓕ/ᑎᕆᓪᓗᓕᐅᑦ': 4,
        'ᒣ/ᓄᕐᕋᓕᐅᑦ': 5,
        'ᔫᓂ/ᒪᓐᓂᓕᐅᑦ': 6,
        'ᔪᓓ/ᑐᕓᔮᕈᑦ': 7,
        'ᐊᐅᒍᔅᑎ/ᐊᐅᔭᓕᕈᑦ': 8,
        'ᓯᑉᑎᒻᐱᕆ/ᐊᒥᕃᔭᐅᑦ': 9,
        'ᐅᒃᑑᐱᕆ/ᓇᑦᔪᐃᔭᕐᕕᒃ': 10,
        'ᓅᕕᒻᐱᕆ/ᐊᕐᓇᓕᖕᖒᑎᕕᒃ': 11,
        'ᑎᓯᒻᐱᕆ/ᐋᒡᔪᓕᐅᑦ': 12,
    }

    ID_1952_DATE = {
        'Januari': 1,
        'Februari': 2,
        'Maret': 3,
        'April': 4,
        'Mei': 5,
        'Juni': 6,
        'Juli': 7,
        'Augustus': 8,
        'September': 9,
        'Oktober': 10,
        'Nopember': 11,
        'Desember': 12,
    }

    IS_1958_DATE = {
        'janúar': 1,
        'febrúar': 2,
        'mars': 3,
        'apríl': 4,
        'maí': 5,
        'júní': 6,
        'júlí': 7,
        'ágúst': 8,
        'september': 9,
        'október': 10,
        'nóvember': 11,
        'desember': 12,
    }

    IT_1960_DATE = {
        'Gennaio': 1,
        'Febbraio': 2,
        'Marzo': 3,
        'April': 4,
        'Maggio': 5,
        'Giugno': 6,
        'Luglio': 7,
        'Agosto': 8,
        'Settembre': 9,
        'Ottobre': 10,
        'Novembre': 11,
        'Dicembre': 12,
    }

    KN_1971_DATE = {
        'ಜನವರಿ': 1,
        'ಫೆಬ್ರುವರಿ': 2,
        'ಮಾರ್ಚ್': 3,
        'ಏಪ್ರಿಲ್': 4,
        'ಮೇ': 5,
        'ಜೂನ್': 6,
        'ಜುಲೈ': 7,
        'ಆಗಸ್ಟ್': 8,
        'ಸೆಪ್ಟೆಂಬರ್': 9,
        'ಅಕ್ಟೋಬರ್': 10,
        'ನವೆಂಬರ್': 11,
        'ಡಿಸೆಂಬರ್': 12,
    }

    KA_1974_DATE = {
        'იანვარი': 1,
        'თებერვალი': 2,
        'მარტი': 3,
        'აპრილი': 4,
        'მაისი': 5,
        'ივნისი': 6,
        'ივლისი': 7,
        'აგვისტო': 8,
        'სექტემბერი': 9,
        'ოქტომბერი': 10,
        'ნოემბერი': 11,
        'დეკემბერი': 12,
    }

    KK_1978_DATE = {
        'Қаңтар': 1,
        'Ақпан': 2,
        'Наурыз': 3,
        'Сәуір': 4,
        'Мамыр': 5,
        'Маусым': 6,
        'Шілде': 7,
        'Тамыз': 8,
        'Қыркүйек': 9,
        'Қазан': 10,
        'Қараша': 11,
        'Желтоқсан': 12,
    }

    KM_1982_DATE = {
        'ខែមករា': 1,
        'ខែកុម្ភៈ': 2,
        'ខែមីនា': 3,
        'ខែមេសា': 4,
        'ខែឧសភា': 5,
        'ខែមិថុនា': 6,
        'ខែកក្កដា': 7,
        'ខែសីហា': 8,
        'ខែកញ្ញា': 9,
        'ខែតុលា': 10,
        'វិច្ឆិកា': 11,
        'ខែធ្នូ': 12,
    }

    RW_1985_DATE = {
        'Mutarama': 1,
        'Gashyantare': 2,
        'Werurwe': 3,
        'Mata': 4,
        'Gicurasi': 5,
        'Kamena': 6,
        'Nyakanga': 7,
        'Kanama': 8,
        'Nzeli': 9,
        'Ukwakira': 10,
        'Ugushyingo': 11,
        'Ukuboza': 12,
    }

    KY_1986_DATE = {
        'Үчтүн айы': 1,
        'Бирдин айы': 2,
        'Жалган куран айы': 3,
        'Чын куран айы': 4,
        'Бугу айы': 5,
        'Кулжа айы': 6,
        'Теке айы': 7,
        'Баш оона айы': 8,
        'Аяк оона айы': 9,
        'Тогуздун айы': 10,
        'Жетинин айы': 11,
        'Бештин айы': 12,
    }

    KO_1991_DATE = {
        '1월': 1,
        '2월': 2,
        '3월': 3,
        '4월': 4,
        '5월': 5,
        '6월': 6,
        '7월': 7,
        '8월': 8,
        '9월': 9,
        '10월': 10,
        '11월': 11,
        '12월': 12,
    }

    KU_2000_DATE = {
        'Rêbendan': 1,
        'Sibat': 2,
        'Adar': 3,
        'Nîsan': 4,
        'Gul': 5,
        'Hezîran': 6,
        'Tirmeh': 7,
        'Tebax': 8,
        'Îlon': 9,
        'Kewçêr': 10,
        'Sermawez': 11,
        'Berfanbar': 12,
        'خاکەلێوە': 1,
        'گوڵان': 2,
        'جۆزەردان': 3,
        'پووشپەڕ': 4,
        'گەلاوێژ': 5,
        'خەرمانان': 6,
        'ڕەزبەر': 7,
        'گەڵاڕێزان': 8,
        'سەرماوەز': 9,
        'بەفرانبار': 10,
        'ڕێبەندان': 11,
        'ڕەشەمە': 12,
        '٠': 0,
        '١': 1,
        '٢': 2,
        '٣': 3,
        '٤': 4,
        '٥': 5,
        '٦': 6,
        '٧': 7,
        '٨': 8,
        '٩': 9,
    }

    LO_2005_DATE = {
        'ມັງກອນ': 1,
        'ກຸມພາ': 2,
        'ມີນາ': 3,
        'ເມສາ': 4,
        'May': 5,
        'ມິຖຸນາ': 6,
        'ກໍລະກົດ': 7,
        'ສິງຫາ': 8,
        'ກັນຍາ': 9,
        'ຕຸລາ': 10,
        'ພະຈິກ': 11,
        'ທັນວາ': 12,
    }

    LA_2006_DATE = {
        'Ianuarius': 1,
        'Februarius': 2,
        'Martius': 3,
        'Aprilis': 4,
        'Maius': 5,
        'Iunius': 6,
        'Iulius': 7,
        'Augustus': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12,
    }

    LV_2007_DATE = {
        'Janvāris': 1,
        'Februāris': 2,
        'Marts': 3,
        'Aprīlis': 4,
        'Maijs': 5,
        'Jūnijs': 6,
        'Jūlijs': 7,
        'Augusts': 8,
        'Septembris': 9,
        'Oktobris': 10,
        'Novembris': 11,
        'Decembris': 12,
    }

    LT_2011_DATE = {
        'Sausio': 1,
        'Vasaris': 2,
        'Kovas': 3,
        'Balandis': 4,
        'Geg.': 5,
        'Birželis': 6,
        'Liepa': 7,
        'Rugpjūtis': 8,
        'Rugsėjis': 9,
        'Spalis': 10,
        'Lapkritis': 11,
        'Gruodis': 12,
    }

    LB_2014_DATE = {
        'Januar': 1,
        'Februar': 2,
        'Mäerz': 3,
        'Abrëll': 4,
        'Mee': 5,
        'Juni': 6,
        'Juli': 7,
        'August': 8,
        'September': 9,
        'Oktober': 10,
        'November': 11,
        'Dezember': 12,
    }

    MK_2022_DATE = {
        'јануари': 1,
        'февруари': 2,
        'март': 3,
        'април': 4,
        'мај': 5,
        'јуни': 6,
        'јули': 7,
        'август': 8,
        'септември': 9,
        'октомври': 10,
        'ноември': 11,
        'декември': 12,
    }

    PT_2122_DATE = {
        'Janeiro': 1,
        'Fevereiro': 2,
        'Março': 3,
        'Abril': 4,
        'Maio': 5,
        'Junho': 6,
        'Julho': 7,
        'Agosto': 8,
        'Setembro': 9,
        'Outubro': 10,
        'Novembro': 11,
        'Dezembro': 12,
        'Jan': 1,
        'Fev': 2,
        'Mar': 3,
        'Abr': 4,
        'Mai': 5,
        'Jun': 6,
        'Jul': 7,
        'Ago': 8,
        'Set': 9,
        'Out': 10,
        'Nov': 11,
        'Dez': 12,
    }

    ES_2181_DATE = {
        'Enero': 1,
        'Febrero': 2,
        'Marzo': 3,
        'Abril': 4,
        'Mayo': 5,
        'Junio': 6,
        'Julio': 7,
        'Agosto': 8,
        'Septiembre': 9,
        'Octubre': 10,
        'Noviembre': 11,
        'Diciembre': 12,
    }

    UR_2238_DATE = {
        'جنوری': 1,
        'فروری': 2,
        'مارچ': 3,
        'اپریل': 4,
        'مئی': 5,
        'جون': 6,
        'جولائی': 7,
        'اگست': 8,
        'ستمبر': 9,
        'اکتوبر': 10,
        'نومبر': 11,
        'دسمبر': 12,
    }

    month = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12,
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Aug': 8,
        'Sept': 9,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12
    }

