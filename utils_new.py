from pathlib import Path
from scapy.layers.dns import DNS
from scapy.layers.inet import TCP
from scapy.packet import Padding
from scapy.utils import rdpcap

# for app identification
PREFIX_TO_APP_ID = {
    # AIM chat: 4 pcap
    'aim_chat_3a': 7,
    'aim_chat_3b': 7,
    'aimchat1': 7,
    'aimchat2': 7,
    # Email: 4 pcap
    'email1a': 16,
    'email1b': 16,
    'email2a': 16,
    'email2b': 16,
    # Facebook: 15 pcap
    'facebook_audio1a': 13,
    'facebook_audio1b': 13,
    'facebook_audio2a': 13,
    'facebook_audio2b': 13,
    'facebook_audio3': 13,
    'facebook_audio4': 13,
    'facebook_chat_4a': 13,
    'facebook_chat_4b': 13,
    'facebook_video1a': 13,
    'facebook_video1b': 13,
    'facebook_video2a': 13,
    'facebook_video2b': 13,
    'facebookchat1': 13,
    'facebookchat2': 13,
    'facebookchat3': 13,
    # FTPS: 4 pcap
    'ftps_down_1a': 6,
    'ftps_down_1b': 6,
    'ftps_up_2a': 6,
    'ftps_up_2b': 6,
    # Gmail: 3 pcap
    'gmailchat1': 17,
    'gmailchat2': 17,
    'gmailchat3': 17,
    # Hangouts: 11 pcap
    'hangout_chat_4b': 14,
    'hangouts_audio1a': 14,
    'hangouts_audio1b': 14,
    'hangouts_audio2a': 14,
    'hangouts_audio2b': 14,
    'hangouts_audio3': 14,
    'hangouts_audio4': 14,
    'hangouts_chat_4a': 14,
    'hangouts_video1b': 14,
    'hangouts_video2a': 14,
    'hangouts_video2b': 14,
    # ICQ: 4 pcap
    'icq_chat_3a': 11,
    'icq_chat_3b': 11,
    'icqchat1': 11,
    'icqchat2': 11,
    # Netflix: 4 pcap
    'netflix1': 0,
    'netflix2': 0,
    'netflix3': 0,
    'netflix4': 0,
    # SCP: 12 pcap
    'scp1': 8,
    'scpdown1': 8,
    'scpdown2': 8,
    'scpdown3': 8,
    'scpdown4': 8,
    'scpdown5': 8,
    'scpdown6': 8,
    'scpup1': 8,
    'scpup2': 8,
    'scpup3': 8,
    'scpup5': 8,
    'scpup6': 8,
    # SFTP: 8 pcap
    'sftp1': 9,
    'sftp_down_3a': 9,
    'sftp_down_3b': 9,
    'sftp_up_2a': 9,
    'sftp_up_2b': 9,
    'sftpdown1': 9,
    'sftpdown2': 9,
    'sftpup1': 9,
    # Skype: 20 pcap
    'skype_audio1a': 4,
    'skype_audio1b': 4,
    'skype_audio2a': 4,
    'skype_audio2b': 4,
    'skype_audio3': 4,
    'skype_audio4': 4,
    'skype_chat1a': 4,
    'skype_chat1b': 4,
    'skype_file1': 4,
    'skype_file2': 4,
    'skype_file3': 4,
    'skype_file4': 4,
    'skype_file5': 4,
    'skype_file6': 4,
    'skype_file7': 4,
    'skype_file8': 4,
    'skype_video1a': 4,
    'skype_video1b': 4,
    'skype_video2a': 4,
    'skype_video2b': 4,
    # Spotify: 4 pcap
    'spotify1': 3,
    'spotify2': 3,
    'spotify3': 3,
    'spotify4': 3,
    # Torrent: 1 pcap
    'torrent01': 12,
    # Tor: 9 pcap
    'torfacebook': 5,
    'torgoogle': 5,
    'tortwitter': 5,
    'torvimeo1': 5,
    'torvimeo2': 5,
    'torvimeo3': 5,
    'toryoutube1': 5,
    'toryoutube2': 5,
    'toryoutube3': 5,
    # Vimeo: 4 pcap
    'vimeo1': 2,
    'vimeo2': 2,
    'vimeo3': 2,
    'vimeo4': 2,
    # Voipbuster: 5 pcap
    'voipbuster1b': 15,
    'voipbuster2b': 15,
    'voipbuster3b': 15,
    'voipbuster_4a': 15,
    'voipbuster_4b': 15,
    # Youtube: 7 pcap
    'youtube1': 1,
    'youtube2': 1,
    'youtube3': 1,
    'youtube4': 1,
    'youtube5': 1,
    'youtube6': 1,
    'youtubehtml5_1': 1,
    # VPN: 27 (-2)
     'vpn_aim_chat1a': 10,
     'vpn_aim_chat1b': 10,
    
     'vpn_bittorrent': 10,
    
     'vpn_email2a': 10,
     'vpn_email2b': 10,
    
     'vpn_facebook_audio2': 10,
     'vpn_facebook_chat1a': 10,
     'vpn_facebook_chat1b': 10,
    
     'vpn_ftps_a': 10,
     'vpn_ftps_b': 10,
    
     'vpn_hangouts_audio1': 10,
     'vpn_hangouts_audio2': 10,
     'vpn_hangouts_chat1a': 10,
     'vpn_hangouts_chat1b': 10,
    
     'vpn_icq_chat1a': 10,
     'vpn_icq_chat1b': 10,
    
     #miss vpn_netflix (too big) [solved]
    'vpn_netflix_a': 10,
    
     'vpn_sftp_a': 10,
    'vpn_sftp_b': 10,
   
     'vpn_skype_audio1': 10,
     'vpn_skype_audio2': 10,
     'vpn_skype_chat1a': 10,
     'vpn_skype_chat1b': 10,
     'vpn_skype_files1a': 10,
     'vpn_skype_files1b': 10,
    
     #miss vpn_spotify [solved]
    'vpn_spotify_a': 10,
    
     'vpn_vimeo_a': 10,
     'vpn_vimeo_b': 10,
    
    # #miss 2 vpn_voibuster
    
     'vpn_youtube_a': 10,


}

ID_TO_APP = {
    0: 'Netflix',
    1: 'Youtube',
    2: 'Vimeo',
    3: 'Spotify',
    4: 'Skype',
    5: 'Tor',
    6: 'FTPS',
    7: 'AIM Chat',
    8: 'SCP',
    9: 'SFTP',
    10: 'VPN',
    11: 'ICQ',
    12: 'Torrent',
    13: 'Facebook',
    14: 'Hangouts',
    15: 'Voipbuster',
    16: 'Email',
    17: 'Gmail'
}

# for traffic identification
PREFIX_TO_TRAFFIC_ID = {
    # Chat
    'aim_chat_3a': 9,
    'aim_chat_3b': 9,
    'aimchat1': 9,
    'aimchat2': 9,
    'facebook_chat_4a': 9,
    'facebook_chat_4b': 9,
    'facebookchat1': 9,
    'facebookchat2': 9,
    'facebookchat3': 9,
    'hangout_chat_4b': 9,
    'hangouts_chat_4a': 9,
    'icq_chat_3a': 9,
    'icq_chat_3b': 9,
    'icqchat1': 9,
    'icqchat2': 9,
    'skype_chat1a': 9,
    'skype_chat1b': 9,
    # Email
    'email1a': 7,
    'email1b': 7,
    'email2a': 7,
    'email2b': 7,
    # File Transfer
    'ftps_down_1a': 0,
    'ftps_down_1b': 0,
    'ftps_up_2a': 0,
    'ftps_up_2b': 0,
    'sftp1': 0,
    'sftp_down_3a': 0,
    'sftp_down_3b': 0,
    'sftp_up_2a': 0,
    'sftp_up_2b': 0,
    'sftpdown1': 0,
    'sftpdown2': 0,
    'sftpup1': 0,
    'skype_file1': 0,
    'skype_file2': 0,
    'skype_file3': 0,
    'skype_file4': 0,
    'skype_file5': 0,
    'skype_file6': 0,
    'skype_file7': 0,
    'skype_file8': 0,
    # Streaming
    'vimeo1': 1,
    'vimeo2': 1,
    'vimeo3': 1,
    'vimeo4': 1,
    'youtube1': 1,
    'youtube2': 1,
    'youtube3': 1,
    'youtube4': 1,
    'youtube5': 1,
    'youtube6': 1,
    'youtubehtml5_1': 1,
    'spotify1': 1,
    'spotify2': 1,
    'spotify3': 1,
    'spotify4': 1,
    'netflix1': 1,
    'netflix2': 1,
    'netflix3': 1,
    'netflix4': 1,
    # Torrent
    'torrent01': 2,
    # VoIP
    'facebook_audio1a': 10,
    'facebook_audio1b': 10,
    'facebook_audio2a': 10,
    'facebook_audio2b': 10,
    'facebook_audio3': 10,
    'facebook_audio4': 10,
    'hangouts_audio1a': 10,
    'hangouts_audio1b': 10,
    'hangouts_audio2a': 10,
    'hangouts_audio2b': 10,
    'hangouts_audio3': 10,
    'hangouts_audio4': 10,
    'skype_audio1a': 10,
    'skype_audio1b': 10,
    'skype_audio2a': 10,
    'skype_audio2b': 10,
    'skype_audio3': 10,
    'skype_audio4': 10,
    # VPN: Chat
    'vpn_aim_chat1a': 6,
    'vpn_aim_chat1b': 6,
    'vpn_facebook_chat1a': 6,
    'vpn_facebook_chat1b': 6,
    'vpn_hangouts_chat1a': 6,
    'vpn_hangouts_chat1b': 6,
    'vpn_icq_chat1a': 6,
    'vpn_icq_chat1b': 6,
    'vpn_skype_chat1a': 6,
    'vpn_skype_chat1b': 6,
    # VPN: File Transfer
    'vpn_ftps_a': 3,
    'vpn_ftps_b': 3,
    'vpn_sftp_a': 3,
    'vpn_sftp_b': 3,
    'vpn_skype_files1a': 3,
    'vpn_skype_files1b': 3,
    # VPN: Email
    'vpn_email2a': 8,
    'vpn_email2b': 8,
    # VPN: Streaming
    'vpn_vimeo_a': 4,
    'vpn_vimeo_b': 4,
    'vpn_youtube_a': 4,
    'vpn_spotify_a': 4,
    'vpn_netflix_a': 4,
    # VPN: Torrent
    'vpn_bittorrent': 5,
    # VPN VoIP
    'vpn_facebook_audio2': 11,
    'vpn_hangouts_audio1': 11,
    'vpn_hangouts_audio2': 11,
    'vpn_skype_audio1': 11,
    'vpn_skype_audio2': 11,
}

ID_TO_TRAFFIC = {
    0: 'File Transfer',
    1: 'Streaming',
    2: 'Torrent',
    3: 'VPN: File Transfer',
    4: 'VPN: Streaming',
    5: 'VPN: Torrent',
    6: 'VPN: Chat',
    7: 'Email',
    8: 'VPN: Email',
    9: 'Chat',
    10: 'Voip',
    11: 'VPN: Voip',
}


def read_pcap(path: Path):
    packets = rdpcap(str(path))

    return packets


def should_omit_packet(packet):
    # SYN, ACK or FIN flags set to 1 and no payload
    if 'TCP' in packet and (packet.flags & 0x13):
        # not payload or contains only padding
        layers = packet[TCP].payload.layers()
        if not layers or (Padding in layers and len(layers) == 1):
            return True

    # DNS segment
    if 'DNS' in packet:
        return True

    return False
