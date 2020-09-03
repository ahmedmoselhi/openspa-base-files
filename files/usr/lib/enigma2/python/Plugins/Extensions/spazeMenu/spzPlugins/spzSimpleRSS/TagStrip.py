from re import sub
entities = [('&#228;', u'\xe4'),
 ('&auml;', u'\xe4'),
 ('&#252;', u'\xfc'),
 ('&uuml;', u'\xfc'),
 ('&#246;', u'\xf6'),
 ('&ouml;', u'\xf6'),
 ('&#196;', u'\xc4'),
 ('&Auml;', u'\xc4'),
 ('&#220;', u'\xdc'),
 ('&Uuml;', u'\xdc'),
 ('&#214;', u'\xd6'),
 ('&Ouml;', u'\xd6'),
 ('&#223;', u'\xdf'),
 ('&szlig;', u'\xdf'),
 ('&#8230;', u'...'),
 ('&#8211;', u'-'),
 ('&#160;', u' '),
 ('&#34;', u'"'),
 ('&#38;', u'&'),
 ('&#39;', u"'"),
 ('&#60;', u'<'),
 ('&#62;', u'>'),
 ('&lt;', u'<'),
 ('&gt;', u'>'),
 ('&nbsp;', u' '),
 ('&amp;', u'&'),
 ('&quot;', u'"'),
 ('&apos;', u"'")]

def strip_readable(html):
    html = html.replace('\n', ' ')
    html = sub('\\s\\s+', ' ', html)
    html = sub('<br(\\s+/)?>', '\n', html)
    html = sub('</?(p|ul|ol)(\\s+.*?)?>', '\n', html)
    html = sub('<li(\\s+.*?)?>', '-', html)
    html = html.replace('</li>', '\n')
    return strip(html)


def strip(html):
    html = sub('<(.*?)>', '', html)
    for escaped, unescaped in entities:
        html = html.replace(escaped, unescaped)

    return html.strip()
