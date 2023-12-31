/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>
#define RECIRCULATE_TIMES 4

/* Define constants for types of packets */
#define PKT_INSTANCE_TYPE_NORMAL 0
#define PKT_INSTANCE_TYPE_INGRESS_CLONE 1
#define PKT_INSTANCE_TYPE_EGRESS_CLONE 2
#define PKT_INSTANCE_TYPE_COALESCED 3
#define PKT_INSTANCE_TYPE_INGRESS_RECIRC 4
#define PKT_INSTANCE_TYPE_REPLICATION 5
#define PKT_INSTANCE_TYPE_RESUBMIT 6

const bit<16> TYPE_IPV4 = 0x800;
const bit<16> TYPE_SRCROUTING = 0x1234;

//Ethernet frame payload padding and P4
//https://github.com/p4lang/p4-spec/issues/587

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header srcRoute_t {
    bit<160>   routeId;
    bit<160>    wId;
}

//header srcWid_t {
    //bit<8>    wId;
//}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
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

struct metadata {
    bit<160>  routeId;
    bit<160>    wId;
    bit<16>   etherType;
    bit<1>    apply_sr;
    bit<1>    apply_decap;
    bit<9>    port;
    bit<9>    f_port;
    bit<9>    count;
    bit<8>    n_bits;
    bit<8>    wport;
}

struct polka_t_top {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
    bit<160>   routeId;
    bit<160>   wId;
}

struct headers {
    ethernet_t  ethernet;
    srcRoute_t  srcRoute;
    //srcWid_t srcWid;
    ipv4_t      ipv4;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        meta.apply_sr = 0;
        transition verify_ethernet;
    }

    state verify_ethernet {
        meta.etherType = packet.lookahead<polka_t_top>().etherType;
        transition select(meta.etherType) {
            TYPE_SRCROUTING: get_routeId;
            default: accept;
        }
    }

    state get_routeId {
	    meta.apply_sr = 1;
        meta.routeId = packet.lookahead<polka_t_top>().routeId;
	    meta.wId = packet.lookahead<polka_t_top>().wId;
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

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action clone_packet(bit<32> mirror_session_id) {
        // Clone from ingress to egress pipeline
        clone(CloneType.I2E, mirror_session_id);
    }

    action srcRoute_nhop() {

        bit<16> nbase=0;
        bit<64> ncount=4294967296*2;
        bit<16> nresult;
        bit<16> nport;

        bit<160>routeid = meta.routeId;

        bit<160>ndata = routeid >> 16;
        bit<16> dif = (bit<16>) (routeid ^ (ndata << 16));

        hash(
            nresult,
            HashAlgorithm.crc16_custom,
            nbase,
            {ndata},ncount
        );

        nport = nresult ^ dif;

        meta.port = (bit<9>) nport;

    }

    action calc_wid() {

        bit<16> wbase=0;
        bit<64> wcount=4294967296*2;
        bit<16> wresult;
        bit<16> wnport;

        bit<160>wid = meta.wId;

        bit<160>wdata = wid >> 16;
        bit<16> dif = (bit<16>) (wid ^ (wdata << 16));

        hash(
            wresult,
            HashAlgorithm.crc16_custom,
            wbase,
            {wdata},wcount
        );

        wnport = wresult ^ dif;

        meta.wport = (bit<8>) wnport;
    } 

    action get_entries() {

    }

    table exact_match {
        key = {
            t_weight: exact;            
        }
        actions = {
            drop;
            get_entries;
        }
        size = 8;   
    }

    apply {
		if (meta.apply_sr==1){
            
		
	    //Calcular Wid 
	    //wID mod nodeID=> t_weight
        t_weight = calc_wid();
           
	    //match t_weight get  index1 and nentries




	    //tstamp =  standard_metadata.ingress_global_timestamp
	   // index2 = index1 + hash(stamp ) mod  nentries
	  // match index2 get
	    
	    
            // Source-routing calculation
           	srcRoute_nhop();

            if(meta.count == 0){
                meta.count = 1;
                meta.n_bits = 0;
            }
            // Porta 1
            if((meta.port & (9w1 << (bit<8>)(meta.count - 1))) > 0){
                if(meta.n_bits == 0){
                    meta.f_port = meta.count;
                }else if(meta.n_bits >= 1){
                    clone_packet((bit<32>)meta.count);
                }
                meta.n_bits = meta.n_bits + 1;
            }
            // Porta 2
            meta.count = meta.count + 1;
            if((meta.port & (9w1 << (bit<8>)(meta.count - 1))) > 0){
                if(meta.n_bits == 0){
                    meta.f_port = meta.count;
                }else if(meta.n_bits >= 1){
                    clone_packet((bit<32>)meta.count);
                }
                meta.n_bits = meta.n_bits + 1;
            }
            // Porta 3
            meta.count = meta.count + 1;
            if((meta.port & (9w1 << (bit<8>)(meta.count - 1))) > 0){
                if(meta.n_bits == 0){
                    meta.f_port = meta.count;
                }else if(meta.n_bits >= 1){
                    clone_packet((bit<32>)meta.count);
                }
                meta.n_bits = meta.n_bits + 1;
            }
            // Porta 4
            meta.count = meta.count + 1;
            if((meta.port & (9w1 << (bit<8>)(meta.count - 1))) > 0){
                if(meta.n_bits == 0){
                    meta.f_port = meta.count;
                }else if(meta.n_bits >= 1){
                    clone_packet((bit<32>)meta.count);
                }
                meta.n_bits = meta.n_bits + 1;
            }
            // Porta 5
            meta.count = meta.count + 1;
            if((meta.port & (9w1 << (bit<8>)(meta.count - 1))) > 0){
                if(meta.n_bits == 0){
                    meta.f_port = meta.count;
                }else if(meta.n_bits >= 1){
                    clone_packet((bit<32>)meta.count);
                }
                meta.n_bits = meta.n_bits + 1;
            }
            // Porta 6
            meta.count = meta.count + 1;
            if((meta.port & (9w1 << (bit<8>)(meta.count - 1))) > 0){
                if(meta.n_bits == 0){
                    meta.f_port = meta.count;
                }else if(meta.n_bits >= 1){
                    clone_packet((bit<32>)meta.count);
                }
                meta.n_bits = meta.n_bits + 1;
            }
            // Porta 7
            meta.count = meta.count + 1;
            if((meta.port & (9w1 << (bit<8>)(meta.count - 1))) > 0){
                if(meta.n_bits == 0){
                    meta.f_port = meta.count;
                }else if(meta.n_bits >= 1){
                    clone_packet((bit<32>)meta.count);
                }
                meta.n_bits = meta.n_bits + 1;
            }
            // Porta 8
            meta.count = meta.count + 1;
            if((meta.port & (9w1 << (bit<8>)(meta.count - 1))) > 0){
                if(meta.n_bits == 0){
                    meta.f_port = meta.count;
                }else if(meta.n_bits >= 1){
                    clone_packet((bit<32>)meta.count);
                }
                meta.n_bits = meta.n_bits + 1;
            }
            standard_metadata.egress_spec = meta.f_port;
		}else{
			drop();
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

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
    apply {  }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {  }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
