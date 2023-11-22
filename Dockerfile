FROM python
ENV semantix_port=7500

COPY BuildManager.py /var
COPY AbstractVirtualCapability.py /var
COPY output.json /var

RUN python -m pip install --upgrade --force-reinstall numpy-quaternion

CMD python /var/BuildManager.py ${semantix_port}
