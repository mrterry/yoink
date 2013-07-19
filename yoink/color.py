import numpy as np


def unpack_last(x):
    x = np.asarray(x)
    shape = x.shape
    return [x[..., i] for i in range(shape[-1])]


def lab2lch(lab):
    l, a, b = unpack_last(lab)

    lch = np.zeros_like(lab)
    lch[:, :, 0] = l  # L
    lch[:, :, 1] = np.sqrt(a**2 + b**2)  # C
    H = lch[:, :, 2]
    H[...] = np.arctan2(b, a)
    H[H < 0] += 2*np.pi  # (-pi, pi) -> (0, 2*pi)
    return lch


def arctan2pi(b, a):
    """np.arctan2 mapped to (0, 2*pi)"""
    ans = np.arctan2(b, a)
    ans = np.where(ans < 0, ans + 2*np.pi, ans)
    assert ans.max() <= 2*np.pi
    assert ans.min() >= 0.
    return ans


def deltaE_cie76(lab1, lab2):
    """
    "just noticible difference" ~ 2.3
    """
    l1, a1, b1 = unpack_last(lab1)
    l2, a2, b2 = unpack_last(lab2)
    return np.sqrt((l2-l1)**2 + (a2-a1)**2 + (b2-b1)**2)


def deltaE_ciede94(lab1, lab2, kC=1, kH=1, kL=1, k1=0.045, k2=0.015):
    """
    kC, kH are weighting factors, usually unity (default)

    kL, k1, k2 depend on the application.  Sample values are:
    kL, k1, k2 = 1, 0.045, 0.015 (graphic arts, default)
    kL, k1, k2 = 2, 0.048, 0.014 (textiles)

    Note: deltaE_ciede94 the defines the scales for the lightness, hue, and
    chroma in terms of the first color.  Consequently
    deltaE_ciede94(lab1, lab2) != deltaE_ciede94(lab2, lab1)
    """
    l1, a1, b1 = unpack_last(lab1)
    l2, a2, b2 = unpack_last(lab2)

    dl = l1 - l2
    c1 = np.sqrt(a1**2 + b1**2)
    c2 = np.sqrt(a2**2 + b2**2)
    da = a1 - a2
    db = b1 - b2
    dc = c1 - c2
    dh_ab = np.sqrt(da**2 + db**2 + dc**2)

    SL = 1
    SC = 1 + k1*c1
    SH = 1 + k2*c1

    ans = (dl/(kL*SL))**2 + (dc/(kC*SC))**2 + (dh_ab/(kH*SH))**2
    return np.sqrt(ans)


def deltaE_ciede2000(lab1, lab2, kL=1, kC=1, kH=1):
    """
    kL = 1  # graphic arts
    kL = 2  # textiles
    """
    l1, a1, b1 = unpack_last(lab1)
    l2, a2, b2 = unpack_last(lab2)

    c1 = np.sqrt(a1**2 + b1**2)
    c2 = np.sqrt(a2**2 + b2**2)

    dl_prime = l2 - l1
    lbar = 0.5*(l1 + l2)
    cbar = 0.5*(c1 + c2)

    c7 = cbar**7
    term = 1 - np.sqrt(c7/(c7 + 25**7))
    a1_prime = a1 * (1 + term/2)
    a2_prime = a2 * (1 + term/2)

    c1_prime = np.sqrt(a1_prime**2 + b1**2)
    c2_prime = np.sqrt(a2_prime**2 + b2**2)
    cbar_prime = 0.5*(c1_prime + c2_prime)
    dc_prime = c2_prime - c1_prime

    # colors are in 360, but atan2 is -180, 180
    # TODO: make h?_prime on (0, 360)
    h1_prime = arctan2pi(b1, a1_prime)
    h2_prime = arctan2pi(b2, a2_prime)

    dh_prime = h2_prime - h1_prime
    mask1 = np.abs(dh_prime) <= np.pi
    mask3 = (-mask1) * (dh_prime > 0)
    mask2 = -(mask1 + mask3)
    dh_prime[mask2] += 2*np.pi
    dh_prime[mask3] -= 2*np.pi

    DH_prime = 2 * np.sqrt(c1_prime * c2_prime) * np.sin(dh_prime/2)

    Hbar_prime = h1_prime + h2_prime
    Hbar_prime += np.where(np.abs(h1_prime - h2_prime) > np.pi, 2*np.pi, 0)
    Hbar_prime *= 0.5

    T = (1 -
         0.17 * np.cos(Hbar_prime - 0.5236) +
         0.32 * np.cos(3*Hbar_prime + 0.1047) -
         0.20 * np.cos(4*Hbar_prime - 1.0996)
         )

    term = (lbar - 30)**2
    SL = 1 + 0.015*term/np.sqrt(20 + term)
    SC = 1 + 0.045*cbar_prime
    SH = 1 + 0.015*cbar_prime * T

    c7 = cbar_prime**7
    term = 1 - np.sqrt(c7/(c7 + 25**7))
    RT = -2 * term * np.sin(1.047 * np.exp(-((Hbar_prime-4.7997)/0.4363)**2))

    l_term = dl_prime / (kL * SL)
    c_term = dc_prime / (kC * SC)
    h_term = DH_prime / (kH * SH)
    r_term = RT * c_term * h_term

    return np.sqrt(l_term**2 + c_term**2 + h_term**2 + r_term)


def deltaE_cmc(lab1, lab2):
    """
    indistinguishable if < 1
    usual value for "different" is > 2

    Note: deltaE_cmc the defines the scales for the lightness, hue, and chroma
    in terms of the first color.  Consequently
    deltaE_cmc(lab1, lab2) != deltaE_cmc(lab2, lab1)
    """
    l1, c1, h1 = unpack_last(lab2lch(lab1))
    l2, c2, h2 = unpack_last(lab2lch(lab2))

    sl = np.where(l1 < 16, 0.511, 0.040975*l1 / (1 + 0.01765*l1))
    sc = 0.638 + 0.0638*c1 / (1 + 0.0131*c1)

    c1_4 = c1**4
    f = np.sqrt(c1_4 / (c1_4 + 1900))
    t = np.where(np.logical_and(h1 >= 2.862, h1 <= 6.021),
                 0.56 * 0.2 * np.abs(np.cos(h1 + 2.93)),
                 0.36 + 0.4 * np.abs(np.cos(h1 + 0.611))
                 )
    sh = sc * (f*t + 1-f)

    l, c = 1, 1
    ans = ((l2 - l1)/(l * sl))**2
    ans += ((c2 - c1)/(c * sc))**2
    deg = np.pi/180.
    ans += ((h2 - h1)*deg/sh)**2  # metric defines h in terms of degrees

    return np.sqrt(ans)
