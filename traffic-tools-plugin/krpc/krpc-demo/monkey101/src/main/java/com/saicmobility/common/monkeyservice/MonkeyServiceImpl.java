package com.saicmobility.common.monkeyservice;

import com.saicmobility.trip.openapi.api.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

@Component
public class MonkeyServiceImpl implements OpenApi {

    private static Logger log = LoggerFactory.getLogger(MonkeyServiceImpl.class);

    @Override
    public OpenQueryPriceRuleRes queryPriceRule(OpenQueryPriceRuleReq openQueryPriceRuleReq) {
        FeeMode fm = FeeMode.newBuilder().setBeginHour("00:00:00").setEndHour("09:00:00").setAmount(1200).build();
        PriceRule pr1 = PriceRule.newBuilder().addFeeMode(fm).build();
        PriceRuleContent c = PriceRuleContent.newBuilder().setProductType("1").addPrices(pr1).build();
        OpenQueryPriceRuleRes res = OpenQueryPriceRuleRes.newBuilder().setContent(c).build();
        return res;
    }

    @Override
    public OpenQueryPriceRuleV2Res queryPriceRuleV2(OpenQueryPriceRuleV2Req openQueryPriceRuleV2Req) {
        return null;
    }

    @Override
    public OpenPriceRes queryEstimateInfo(OpenPriceReq openPriceReq) {
        return null;
    }

    @Override
    public OpenCreateRes createOrder(OpenCreateReq openCreateReq) {
        return null;
    }

    @Override
    public OpenCancelRes cancelOrder(OpenCancelReq openCancelReq) {
        return null;
    }

    @Override
    public OpenLocationRes queryDriverLocation(OpenLocationReq openLocationReq) {
        return null;
    }

    @Override
    public OpenDetailRes queryOrderDetail(OpenDetailReq openDetailReq) {
        return null;
    }

    @Override
    public OpenBillRes queryBillingDetails(OpenBillReq openBillReq) {
        return null;
    }

    @Override
    public OpenApplyInvoiceRes applyInvoice(OpenApplyInvoiceReq openApplyInvoiceReq) {
        return null;
    }

    @Override
    public OpenQueryInvoiceRes queryInvoice(OpenQueryInvoiceReq openQueryInvoiceReq) {
        return null;
    }

    @Override
    public OpenResendInvoiceRes resendInvoice(OpenResendInvoiceReq openResendInvoiceReq) {
        return null;
    }

    @Override
    public OpenPayStatusRes payStatus(OpenPayStatusReq openPayStatusReq) {
        return null;
    }

    @Override
    public OpenComplaintRes complaint(OpenComplaintReq openComplaintReq) {
        return null;
    }

    @Override
    public OrderEventNotifyRes orderEventNotifyByMerchant(OrderEventNotifyReq orderEventNotifyReq) {
        return null;
    }

    @Override
    public OpenEvaluateDriverRes evaluateDriver(OpenEvaluateDriverReq openEvaluateDriverReq) {
        return null;
    }

    @Override
    public OpenQueryOrderListRes queryOrderList(OpenQueryOrderListReq openQueryOrderListReq) {
        return null;
    }

    @Override
    public QueryNearByDriverRes queryNearByDriver(QueryNearByDriverReq queryNearByDriverReq) {
        return null;
    }

    @Override
    public InvalidInvoiceRes cancelInvoice(InvalidInvoiceReq invalidInvoiceReq) {
        return null;
    }

    @Override
    public QueryInvoicedAmountRes queryInvoiceAmount(QueryInvoicedAmountReq queryInvoicedAmountReq) {
        return null;
    }

    @Override
    public OpenQueryCancelRuleRes queryCancelRule(OpenQueryCancelRuleReq openQueryCancelRuleReq) {
        return null;
    }

    @Override
    public OpenCreateV2Res createOrderV2(OpenCreateV2Req openCreateV2Req) {
        return null;
    }

    @Override
    public OpenPriceV2Res queryEstimateInfoV2(OpenPriceV2Req openPriceV2Req) {
        return null;
    }

    @Override
    public ModifyDestinationRes modifyDestination(ModifyDestinationReq modifyDestinationReq) {
        return null;
    }

    @Override
    public OpenQueryCitiesRes queryCities(OpenQueryCitiesReq openQueryCitiesReq) {
        return null;
    }

    @Override
    public OpenQueryCityCodeRes queryCityCode(OpenQueryCityCodeReq openQueryCityCodeReq) {
        return null;
    }

    @Override
    public OpenQueryVirtualPhoneNoRes queryVirtualPhoneNo(OpenQueryVirtualPhoneNoReq openQueryVirtualPhoneNoReq) {
        return null;
    }

    @Override
    public QueryTracesByOrderNoRes queryTracesByOrderNo(QueryTracesByOrderNoReq queryTracesByOrderNoReq) {
        return null;
    }

    @Override
    public CondemnNotifyBySaicRes condemnNotifyBySaic(CondemnNotifyBySaicReq condemnNotifyBySaicReq) {
        return null;
    }

    @Override
    public BindDriverVirtualRes bindDriverVirtualMobile(BindDriverVirtualReq bindDriverVirtualReq) {
        return null;
    }

    @Override
    public OpenQueryCancelRuleV2Res queryCancelRuleV2(OpenQueryCancelRuleV2Req openQueryCancelRuleV2Req) {
        return null;
    }

    @Override
    public SetCancelReasonByPassengerRes setCancelReasonByPassenger(SetCancelReasonByPassengerReq setCancelReasonByPassengerReq) {
        return null;
    }

    @Override
    public BatchAddEntUserRes batchAddEntUser(BatchAddEntUserReq batchAddEntUserReq) {
        return null;
    }

    @Override
    public BatchDelEntUserRes batchDelEntUser(BatchDelEntUserReq batchDelEntUserReq) {
        return null;
    }

    @Override
    public QueryEntUserListRes queryEntUserList(QueryEntUserListReq queryEntUserListReq) {
        return null;
    }

    @Override
    public SyncRefundRes syncRefund(SyncRefundReq syncRefundReq) {
        return null;
    }

    @Override
    public SetDestInfoRes setDestInfo(SetDestInfoReq setDestInfoReq) {
        return null;
    }

    @Override
    public OpenBatchDetailRes openBatchDetail(OpenBatchDetailReq openBatchDetailReq) {
        return null;
    }

    @Override
    public SyncPayNotifyRes syncPayNotify(SyncPayNotifyReq syncPayNotifyReq) {
        return null;
    }

    @Override
    public QueryOrderForCSRes queryOrderForCS(QueryOrderForCSReq queryOrderForCSReq) {
        return null;
    }

    @Override
    public CreateEnterpriseRes createEnterprise(CreateEnterpriseReq createEnterpriseReq) {
        return null;
    }

    @Override
    public ShieldingDriverRes shieldingDriver(ShieldingDriverReq shieldingDriverReq) {
        return null;
    }

    @Override
    public RmShieldingDriverRes rmShieldingDriver(RmShieldingDriverReq rmShieldingDriverReq) {
        return null;
    }

    @Override
    public CreateEntApplicationRes createEntApplication(CreateEntApplicationReq createEntApplicationReq) {
        return null;
    }

    @Override
    public QueryOrderListV2Res queryOrderListV2(QueryOrderListV2Req queryOrderListV2Req) {
        return null;
    }

    @Override
    public QueryRealTimePriceV2Res queryRealTimePriceV2(QueryRealTimePriceV2Req queryRealTimePriceV2Req) {
        return null;
    }

    @Override
    public QueryPriceRuleGaoDeRes queryPriceRuleGaoDe(QueryPriceRuleGaoDeReq queryPriceRuleGaoDeReq) {
        return null;
    }

    @Override
    public SendThirdCompensateRes syncThirdCompensate(SendThirdCompensateReq sendThirdCompensateReq) {
        return null;
    }

    @Override
    public OpenCreateStdRes createOrderStd(OpenCreateStdReq openCreateStdReq) {
        return null;
    }

    @Override
    public ModifyContactRes modifyContact(ModifyContactReq modifyContactReq) {
        return null;
    }

    @Override
    public QueryOrderStatusRes queryOrderStatus(QueryOrderStatusReq queryOrderStatusReq) {
        return null;
    }

    @Override
    public OpenCancelOderIsDutyRes cancelOderIsDuty(OpenCancelOderIsDutyReq openCancelOderIsDutyReq) {
        return null;
    }

    @Override
    public OpenConfirmExtraFeeRes confirmExtraFee(OpenConfirmExtraFeeReq openConfirmExtraFeeReq) {
        return null;
    }

    @Override
    public OpenContinueRes continueOrder(OpenContinueReq openContinueReq) {
        return null;
    }

    @Override
    public OpenQueryNearCarRes queryNearCar(OpenQueryNearCarReq openQueryNearCarReq) {
        return null;
    }

    @Override
    public OpenQueryRealTimePriceRes queryRealTimePrice(OpenQueryRealTimePriceReq openQueryRealTimePriceReq) {
        return null;
    }
}


