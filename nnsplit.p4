/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

/* CONSTANTS */

const bit<16> TYPE_IPV4 = 0x800;
const bit<16> TYPE_SOREN = 0x8845;
const bit<8>  TYPE_TCP  = 6;

#define CONST_MAX_PORTS 	32
#define CONST_MAX_LABELS 	10
#define REGISTER_LENGTH 255

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<13> switch_id_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header soren_t {
    bit<56>    val;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    tos;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header tcp_t{
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<4>  res;
    bit<1>  cwr;
    bit<1>  ece;
    bit<1>  urg;
    bit<1>  ack;
    bit<1>  psh;
    bit<1>  rst;
    bit<1>  syn;
    bit<1>  fin;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;

}

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> length_;
    bit<16> checksum;
}


struct headers {
    ethernet_t          ethernet;
    soren_t             soren;
    ipv4_t              ipv4;
    tcp_t               tcp;
    udp_t               udp;
}



struct metadata {
    bit<1> is_ingress_border;
    bit<1> is_egress_border;

}


/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {

        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType){
            TYPE_SOREN: parse_soren;
            TYPE_IPV4: ipv4;
            default: accept;
        }
    }

    state parse_soren {
        packet.extract(hdr.soren);
        transition ipv4;
    }

    state ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            17: parse_udp;
            6:  parse_tcp;
            default: accept;
        }
    }

    state parse_tcp {
        packet.extract(hdr.tcp);
        transition accept;
    }

    state parse_udp {
        packet.extract(hdr.udp);
        transition accept;
    }

}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {


    register<bit<56>>(100) weights_bnn;
    bit<56> bnn_input = 0;
    bit<56> XNOROutput = 0;
    bit<56> NextLayerInput = 0;
    bit<5> output_result = 0;

    bit<1> activated = 0;
    bit<64> m1 = 0x5555555555555555;
    bit<64> m2 = 0x3333333333333333;
    bit<64> m4 = 0x0f0f0f0f0f0f0f0f;
    bit<64> m8 = 0x00ff00ff00ff00ff;
    bit<64> m16= 0x0000ffff0000ffff;
    bit<64> m32= 0x00000000ffffffff;
    //bit<128> m64= 0x0000000000000000ffffffffffffffff;

    bit<16> L4src = 0;
    bit<16> L4dst = 0;

    // input: proto, srcport, dstport, packet len
    action BuildInput(){
        bnn_input = ((bit<56>)hdr.ipv4.protocol)<<16;
        bnn_input = (bnn_input + (bit<56>)L4src)<<16;
        bnn_input = (bnn_input + (bit<56>)L4dst)<<16;
        bnn_input = (bnn_input + (bit<56>)hdr.ipv4.totalLen);
    }

    action XNOR(bit<56> weight){
        XNOROutput = weight^bnn_input;
        XNOROutput = ~XNOROutput;
    }

    action BitCount(bit<56> bitInput){
        bit<64> x= (bit<64>)bitInput;
	    x = (x & m1 ) + ((x >>  1) & m1 );
	    x = (x & m2 ) + ((x >>  2) & m2 );
	    x = (x & m4 ) + ((x >>  4) & m4 );
	    x = (x & m8 ) + ((x >>  8) & m8 );
	    x = (x & m16) + ((x >> 16) & m16);
	    x = (x & m32) + ((x >> 32) & m32);

        activated = (x>29) ? (bit<1>)1 : 0;
        NextLayerInput = NextLayerInput<<1;
        NextLayerInput = NextLayerInput + (bit<56>)activated;

    }

    action LayerProcess(bit<10> offset){
        bit<56> weight = 0;
        NextLayerInput = 0;
        weights_bnn.read(weight, (bit<32>)offset+0);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+1);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+2);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+3);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+4);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+5);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+6);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+7);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+8);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+9);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+10);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+11);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+12);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+13);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+14);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+15);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+16);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+17);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+18);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+19);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+20);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+21);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+22);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+23);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+24);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+25);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+26);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+27);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+28);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+29);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+30);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+31);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+32);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+33);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+34);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+35);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+36);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+37);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+38);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+39);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+40);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+41);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+42);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+43);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+44);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+45);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+46);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+47);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+48);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+49);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+50);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+51);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+52);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+53);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+54);
        XNOR(weight);
        BitCount(XNOROutput);
        weights_bnn.read(weight, (bit<32>)offset+55);
        XNOR(weight);
        BitCount(XNOROutput);
    }

    action check_switch_id(switch_id_t swid){
        if (swid == 1){
            meta.is_ingress_border = (bit<1>)1;

        }
        if (swid == 5) {
            meta.is_egress_border = (bit<1>)1;
        }
    }

    table check_swid {
        actions = {
            check_switch_id;
            NoAction;
        }
        default_action = NoAction();
    }


    action add_soren_header() {
        hdr.soren.setValid();
        hdr.soren.val = 0;
        hdr.ethernet.etherType = TYPE_SOREN;
    }

    action drop() {
        mark_to_drop(standard_metadata);
    }


    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;

        standard_metadata.egress_spec = port;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
        }
        default_action = drop;
        size = 128;
    }

    apply {
        check_swid.apply();

        if (hdr.udp.isValid()){
            L4src=hdr.udp.srcPort;
            L4dst=hdr.udp.dstPort;
        }

        if (hdr.tcp.isValid()){
            L4src=hdr.tcp.srcPort;
            L4dst=hdr.tcp.dstPort;
        }

        if (meta.is_ingress_border == 1 && standard_metadata.ingress_port == 1) {
            if (hdr.ipv4.isValid()){

                 add_soren_header();

                 if (hdr.soren.val == 0){
                     hdr.soren.val = (bit<56>)1;
                     BuildInput();
                     weights_bnn.write(70, bnn_input);

                     LayerProcess(0);

                     weights_bnn.write(71, NextLayerInput);

                     hdr.soren.val = NextLayerInput;

                 }
            }
        }

        else if (hdr.soren.isValid()){

             if (hdr.soren.val != 0){
                 bnn_input = hdr.soren.val;
                 LayerProcess(0);
                 weights_bnn.write(73, NextLayerInput);
                 hdr.soren.val = NextLayerInput;
             }

      }
      if (meta.is_egress_border == 1){

          if(hdr.soren.isValid()){
               bit<56> soren_val = hdr.soren.val;
                digest(1, soren_val);
                hdr.soren.setInvalid();
                hdr.ethernet.etherType = TYPE_IPV4;

                weights_bnn.write(98, hdr.soren.val);

            }

           }


        if(hdr.soren.isValid()){
            ipv4_lpm.apply();
        }

        // We implement normal forwarding
         else if (hdr.ipv4.isValid()){
            ipv4_lpm.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {


    apply {

    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {
	update_checksum(
	    hdr.ipv4.isValid(),
            { hdr.ipv4.version,
	            hdr.ipv4.ihl,
              hdr.ipv4.tos,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}


/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {

        //parsed headers have to be added again into the packet.
        packet.emit(hdr.ethernet);
        packet.emit(hdr.soren);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.tcp);
        packet.emit(hdr.udp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

//switch architecture
V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
