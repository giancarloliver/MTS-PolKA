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

enum bit<8> FieldLists {
    resubmit_fl1 = 0
}

struct mymeta_t {
    @field_list(FieldLists.resubmit_fl1)
    bit<3>   resubmit_reason;
    @field_list(FieldLists.resubmit_fl1)
    bit<9> f1;
}

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
    bit<160>  wId;
    bit<16>   etherType;
    bit<1>    apply_sr;
    bit<1>    apply_decap;
    bit<9>    port;
    bit<9>    f_port;
    bit<9>    count;
    bit<8>    n_bits;
    bit<9>    wport;
    bit<9>  t_weight;
    bit<16>   index2;   
    bit<9> port_position;
    bit<1> continue_bit;
    bit<9> active_port_count;      
    mymeta_t mymeta;
}

#define MAX_PORTS 10

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

    direct_counter(CounterType.packets_and_bytes) direct_port_counter;
    counter(MAX_PORTS, CounterType.packets) ingress_port_counter;
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action clone_packet(bit<32> mirror_session_id) {
        // Clone from ingress to egress pipeline
        clone(CloneType.I2E, mirror_session_id);
    }
  

   
    action calc_wid() {

        bit<16> wbase=0;
        bit<64> wcount=4294967297*2;
        bit<16> wresult;
        bit<16> wnport;

        bit<160>wid = meta.wId;

        bit<160>wdata = wid >> 16;
        bit<16> wdif = (bit<16>) (wid ^ (wdata << 16));

        hash(
            wresult,
            HashAlgorithm.crc16_custom,
            wbase,
            {wdata},wcount
        );

        wnport = wresult ^ wdif;

        meta.t_weight = (bit<9>) wnport; 
                 
    } 

    action do_resubmit_reason1() {
        meta.mymeta.resubmit_reason = 1;
        meta.mymeta.f1 = meta.port;
        resubmit_preserving_field_list((bit<8>)FieldLists.resubmit_fl1);
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

    action get_entries(bit<16> index1, bit<16> nentries) {

        bit<16> nresult;               
              
        hash(nresult,
            HashAlgorithm.crc16,
            index1,
            {standard_metadata.ingress_global_timestamp},nentries            
        );
                    
        meta.index2 = nresult;

    }
    action get_port_position(bit<9>  port_position) {       
           
        meta.port_position = port_position;
    }

   
    table exact_match {
        key = {
            meta.t_weight: exact;            
        }
        actions = {
            drop;
            get_entries;
        }
        size = 1024;   
    }

    table multipath {

        key = {
            meta.index2: exact;
        }
        actions = {
            drop; 
            get_port_position;          
        }
        counters = direct_port_counter;
         size = 1024;
    }   

    apply {
        ingress_port_counter.count((bit<32>) standard_metadata.ingress_port);                
		if (meta.apply_sr==1){

            if (meta.mymeta.resubmit_reason != 1) {
                srcRoute_nhop();   
                do_resubmit_reason1();
            } else if (meta.mymeta.resubmit_reason == 1) {                      
                meta.port = meta.mymeta.f1;
                
                calc_wid(); 
                exact_match.apply();              
                multipath.apply();          
                   
             
                meta.count = 1;
                meta.continue_bit = 1; 
                meta.active_port_count = 0;

                    // Porta 1
                if(((meta.port & (9w1 << (bit<8>)(meta.count - 1))) > 0) && (meta.continue_bit == 1)) {
                    meta.active_port_count = meta.active_port_count + 1;
                    if(meta.active_port_count == meta.port_position){
                        meta.f_port = meta.count;
                        meta.continue_bit = 0;
                    }                
                }
                // Porta 2
                meta.count = meta.count + 1;
                if(((meta.port & (9w1 << (bit<8>)(meta.count - 1))) > 0) && (meta.continue_bit == 1)) {
                    meta.active_port_count = meta.active_port_count + 1;
                    if(meta.active_port_count == meta.port_position){
                        meta.f_port = meta.count;
                        meta.continue_bit = 0;                    
                    }                
                }
                // Porta 3
                meta.count = meta.count + 1;
                if(((meta.port & (9w1 << (bit<8>)(meta.count - 1))) > 0) && (meta.continue_bit == 1)) {
                    meta.active_port_count = meta.active_port_count + 1;
                    if(meta.active_port_count == meta.port_position){
                        meta.f_port = meta.count;
                        meta.continue_bit = 0;                    
                    }                
                }
                // Porta 4
                meta.count = meta.count + 1;
                if(((meta.port & (9w1 << (bit<8>)(meta.count - 1))) > 0) && (meta.continue_bit == 1)) {
                    meta.active_port_count = meta.active_port_count + 1;
                    if(meta.active_port_count == meta.port_position){
                        meta.f_port = meta.count;
                        meta.continue_bit = 0;                    
                    }                
                }
                // Porta 5
                meta.count = meta.count + 1;
                if(((meta.port & (9w1 << (bit<8>)(meta.count - 1))) > 0) && (meta.continue_bit == 1)) {
                    meta.active_port_count = meta.active_port_count + 1;
                    if(meta.active_port_count == meta.port_position){
                        meta.f_port = meta.count;
                        meta.continue_bit = 0;                    
                    }                
                }
                // Porta 6
                meta.count = meta.count + 1;
                if(((meta.port & (9w1 << (bit<8>)(meta.count - 1))) > 0) && (meta.continue_bit == 1)) {
                    meta.active_port_count = meta.active_port_count + 1;
                    if(meta.active_port_count == meta.port_position){
                        meta.f_port = meta.count;
                        meta.continue_bit = 0;                    
                    }                
                }
                // Porta 7
                meta.count = meta.count + 1;
                if(((meta.port & (9w1 << (bit<8>)(meta.count - 1))) > 0) && (meta.continue_bit == 1)) {
                    meta.active_port_count = meta.active_port_count + 1;
                    if(meta.active_port_count == meta.port_position){
                        meta.f_port = meta.count;
                        meta.continue_bit = 0;                    
                    }                
                }
                // Porta 8
                meta.count = meta.count + 1;
                if(((meta.port & (9w1 << (bit<8>)(meta.count - 1))) > 0) && (meta.continue_bit == 1)) {
                    meta.active_port_count = meta.active_port_count + 1;
                    if(meta.active_port_count == meta.port_position){
                        meta.f_port = meta.count;
                        meta.continue_bit = 0;                    
                    }                
                }       
                standard_metadata.egress_spec = meta.f_port; 
            }
                                 
		}
        else{
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
    counter(MAX_PORTS, CounterType.packets) egress_port_counter;
    apply {  
        egress_port_counter.count((bit<32>) standard_metadata.egress_port);
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
