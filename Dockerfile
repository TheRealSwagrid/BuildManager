FROM python
ENV semantix_port=7500

COPY BuildManager.py /var
COPY AbstractVirtualCapability.py /var
COPY output.json /var

CMD python /var/BuildManager.py ${semantix_port}
