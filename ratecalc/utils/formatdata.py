def format_lightcurve_data(phase, mags, labels):
    format_str = '{:>8.3f}   '
    format_str += '   '.join(['{:>7.2f}' for k in range(len(labels))])
    out = ['# time    ' + '    '.join(labels)]
    for k in xrange(len(phase)):
        data = [phase[k]] + [m[k] for m in mags]
        out.append(format_str.format(*data))

    return '\n'.join(out)


def format_expected_data(mag, n, labels):
    format_str = '{:>7.2f}   '
    format_str += '   '.join(['{:>7.2e}' for k in range(len(n))])
    out = ['# m_lim    ' + '    '.join(['n_%s'%(l.replace(' ', '_'))
                                                for l in labels])]
    for k in xrange(len(mag)):
        data = [mag[k]] + [n_[k] for n_ in n]
        out.append(format_str.format(*data))

    return '\n'.join(out)
        
def format_redshift_data(z, n):
    format_str = '{:>5.3f}   {:>7.2e}'
    out = ['# z_bincenter n_transient']
    for k in xrange(len(z)):
        out.append(format_str.format(z[k], n[k]))

    return '\n'.join(out)