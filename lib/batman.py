import subprocess
import json
import re


class Batman(object):
    """
    Bindings for B.A.T.M.A.N. Advanced
    commandline interface "batctl"
    """
    def __init__(self, mesh_interface='bat0', alfred_sockpath=None):
        self.mesh_interface = mesh_interface
        self.alfred_sock = alfred_sockpath

        # compile regular expressions only once on startup
        self.mac_addr_pattern = re.compile(r'(([a-z0-9]{2}:){5}[a-z0-9]{2})')

    def vis_data(self):
        return self.vis_data_batadv_vis()

    @staticmethod
    def vis_data_helper(lines):
        vd_tmp = []
        for line in lines:
            try:
                utf8_line = line.decode('utf-8')
                vd_tmp.append(json.loads(utf8_line))
            except UnicodeDecodeError:
                pass
        return vd_tmp

    def vis_data_batadv_vis(self):
        """
        Parse "batadv-vis -i <mesh_interface> -f json"
        into an array of dictionaries.
        """
        cmd = ['batadv-vis', '-i', self.mesh_interface, '-f', 'json']
        if self.alfred_sock:
            cmd.extend(['-u', self.alfred_sock])
        output = subprocess.check_output(cmd)
        lines = output.splitlines()
        return self.vis_data_helper(lines)

    def gateway_list(self):
        """
        Parse "batctl -m <mesh_interface> gwl -n"
        into an array of dictionaries.
        """
        output = subprocess.check_output(
            ['batctl', '-m', self.mesh_interface, 'gwl', '-n'])
        output_utf8 = output.decode('utf-8')
        rows = output_utf8.splitlines()

        gateways = []

        # local gateway
        header = rows.pop(0)
        mode, bandwidth = self.gateway_mode()
        if mode == 'server':
            local_gw_mac = self.mac_addr_pattern.search(header).group(0)
            gateways.append(local_gw_mac)

        # remote gateway(s)
        for row in rows:
            match = self.mac_addr_pattern.search(row)
            if match:
                gateways.append(match.group(1))

        return gateways

    def gateway_mode(self):
        """
        Parse "batctl -m <mesh_interface> gw"
        return: tuple mode, bandwidth, if mode != server then bandwidth is None
        """
        output = subprocess.check_output(
            ['batctl', '-m', self.mesh_interface, 'gw'])
        chunks = output.decode("utf-8").split()

        return chunks[0], chunks[3] if 3 in chunks else None

if __name__ == "__main__":
    bc = Batman()
    vd = bc.vis_data()
    gw = bc.gateway_list()
    for x in vd:
        print(x)
    print(gw)
    print(bc.gateway_mode())
