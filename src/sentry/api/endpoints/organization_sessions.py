from __future__ import absolute_import

from rest_framework.response import Response

import sentry_sdk

from sentry.api.bases import OrganizationEventsV2EndpointBase
from sentry.snuba.sessions_v2 import (
    QueryDefinition,
    run_sessions_query,
    massage_sessions_result,
)


class OrganizationSessionsEndpoint(OrganizationEventsV2EndpointBase):
    def get(self, request, organization):
        # with self.handle_query_errors():
        query = self.build_sessions_query(request, organization)

        with sentry_sdk.start_span(op="sessions.endpoint", description="run_sessions_query"):
            result_totals, result_timeseries = run_sessions_query(query)

        # print(result_totals, result_timeseries)

        with sentry_sdk.start_span(op="sessions.endpoint", description="massage_sessions_result"):
            result = massage_sessions_result(query, result_totals, result_timeseries)
        return Response(result, status=200)

    def build_sessions_query(self, request, organization):
        with sentry_sdk.start_span(op="sessions.endpoint", description="build_sessions_query"):
            params = self.get_snuba_params(request, organization, check_global_views=False)

            return QueryDefinition(request, params)
