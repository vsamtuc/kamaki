:param  Copyright 2013 GRNET S.A. All rights reserved.
:param 
:param  Redistribution and use in source and binary forms, with or
:param  without modification, are permitted provided that the following
:param  conditions are met:
:param 
:param    1. Redistributions of source code must retain the above
:param       copyright notice, this list of conditions and the following
:param       disclaimer.
:param 
:param    2. Redistributions in binary form must reproduce the above
:param       copyright notice, this list of conditions and the following
:param       disclaimer in the documentation and/or other materials
:param       provided with the distribution.
:param 
:param  THIS SOFTWARE IS PROVIDED BY GRNET S.A. ``AS IS'' AND ANY EXPRESS
:param  OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
:param  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
:param  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL GRNET S.A OR
:param  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
:param  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
:param  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
:param  USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
:param  AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
:param  LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
:param  ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
:param  POSSIBILITY OF SUCH DAMAGE.
:param 
:param  The views and conclusions contained in the software and
:param  documentation are those of the authors and should not be
:param  interpreted as representing official policies, either expressed
:param  or implied, of GRNET S.A.

from kamaki.clients import ClientError
from kamaki.clients.networking.rest_api import NetworkingRestClient


class NetworkingClient(NetworkingRestClient):
    """OpenStack Network API 2.0 client"""

    def list_networks(self):
        r = self.networks_get(success=200)
        return r.json['networks']

    def create_network(self, name, admin_state_up=None, shared=None):
        req = dict(network=dict(
            name=name, admin_state_up=bool(admin_state_up)))
        if shared not in (None, ):
            req['network']['shared'] = bool(shared)
        r = self.networks_post(json_data=req, success=201)
        return r.json['network']

    def create_networks(self, networks):
        """Atomic operation for batch network creation (all or nothing)
        :param networks: (list) [
            {name: ..(str).., admin_state_up: ..(bool).., shared: ..(bool)..},
            {name: ..(str).., admin_state_up: ..(bool).., shared: ..(bool)..}]
            name is mandatory, the rest is optional
            e.g., create_networks([
                {name: 'net1', admin_state_up: True},
                {name: 'net2'}])
        :returns: (list of dicts) created networks details
        :raises ValueError: if networks is misformated
        :raises ClientError: if the request failed or didn't return 201
        """
        try:
            msg = 'The networks parameter must be list or tuple'
            assert (
                isinstance(networks, list) or isinstance(networks, tuple)), msg
            for network in networks:
                msg = 'Network specification %s is not a dict' % network
                assert isinstance(network, dict), msg
                err = set(network).difference(
                    ('name', 'admin_state_up', 'shared'))
                if err:
                    raise ValueError(
                        'Invalid key(s): %s in network specification %s' % (
                            err, network))
                msg = 'Name is missing in network specification: %s' % network
                assert network.get('name', None), msg
                network.setdefault('admin_state_up', False)
        except AssertionError as ae:
            raise ValueError('%s' % ae)

        req = dict(networks=list(networks))
        r = self.networks_post(json_data=req, success=201)
        return r.json['networks']

    def get_network_details(self, network_id):
        r = self.networks_get(network_id, success=200)
        return r.json['network']

    def update_network(
            self, network_id, name=None, admin_state_up=None, shared=None):
        network = dict()
        if name:
            network['name'] = name
        if admin_state_up not in (None, ):
            network['admin_state_up'] = admin_state_up
        if shared not in (None, ):
            network['shared'] = shared
        network = dict(network=network)
        r = self.networks_put(network_id, json_data=network, success=200)
        return r.json['network']

    def delete_network(self, network_id):
        r = self.networks_delete(network_id, success=204)
        return r.headers

    def list_subnets(self):
        r = self.subnets_get(success=200)
        return r.json['subnets']

    def create_subnet(
            self, network_id, cidr,
            name=None, allocation_pools=None, gateway_ip=None, subnet_id=None
            ipv6=None, endble_dhcp=None):
        """
        :param network_id: (str)
        :param cidr: (str)

        :param name: (str) The subnet name
        :param allocation_pools: (list of dicts) start/end addresses of
            allocation pools: [{'start': ..., 'end': ...}, ...]
        :param gateway_ip: (str)
        :param subnet_id: (str)
        :param ipv6: (bool) ip_version == 6 if true else 4 (default)
        :param enable_dhcp: (bool)
        """
        subnet = dict(
            network_id=network_id, cidr=cidr, ip_version=6 if ipv6 else 4)
        if name:
            subnet['name'] = name
        if allocation_pools:
            subnet['allocation_pools'] = allocation_pools
        if gateway_ip:
            subnet['gateway_ip'] = gateway_ip
        if subnet_id:
            subnet['id'] = subnet_id
        if enable_dhcp not in (None, ):
            subnet['enable_dhcp'] = bool(enable_dhcp)
        r = self.subnets_post(json_data=dict(subnet=subnet), success=201)
        return r.json['subnet']

    def create_subnets(self, subnets):
        """Atomic operation for batch subnet creation (all or nothing)
        :param subnets: (list of dicts) {key: ...} with all parameters in the
            method create_subnet, where method mandatory / optional paramteres
            respond to mandatory / optional paramters in subnets items
        :returns: (list of dicts) created subnetss details
        :raises ValueError: if subnets parameter is incorrectly formated
        :raises ClientError: if the request failed or didn't return 201
        """
        try:
            msg = 'The subnets parameter must be list or tuple'
            assert (
                isinstance(subnets, list) or isinstance(subnets, tuple)), msg
            for subnet in subnets:
                msg = 'Subnet specification %s is not a dict' % subnet
                assert isinstance(subnet, dict), msg
                err = set(subnet).difference((
                    'network_id', 'cidr', 'name', 'allocation_pools',
                    'gateway_ip', 'subnet_id', 'ipv6', 'endble_dhcp'))
                if err:
                    raise ValueError(
                        'Invalid key(s): %s in subnet specification %s' % (
                            err, subnet))
                msg = 'network_id is missing in subnet spec: %s' % subnet
                assert subnet.get('network_id', None), msg
                msg = 'cidr is missing in subnet spec: %s' % subnet
                assert subnet.get('cidr', None), msg
                subnet['ip_version'] = 6 if subnet.pop('ipv6', None) else 4
        except AssertionError as ae:
            raise ValueError('%s' % ae)

        r = self.subnets_post(json_data=dict(subnets=subnets), success=201)
        return r.json['subnets']
