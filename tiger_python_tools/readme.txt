    public int MustSendMsgLoop(RedisHelper r, IMongoDatabase mongodb)
    {
        List<string> rclist = new List<string>();
        if (m_mustsendmsgs != null)
        {
            lock (m_mustsendmsgs)
            {
                foreach (MustSendMsgData m in m_mustsendmsgs.Values)
                {
                    if (m.sendstatus == MustSendMsgData.SendStatus.WAIT)
                    {
                        if (isOnLine())
                        {
                            AsyncSendMsg(m.msgid, m.msgdm, m.msgflowid);
                            m.sendstatus = MustSendMsgData.SendStatus.SENDING;
                            m.eventtime = DateTime.Now;
                            m.sendcount++;
                        }
                        else
                        {
                            if ((DateTime.Now - m.eventtime).TotalSeconds > 30)
                            {
                                m.eventtime = DateTime.Now;
                                string h = r.GetStringKey("h" + m_key);
                                if (h == Program.g_savedguid)
                                {
                                    //暂时离线
                                }
                                else
                                {
                                    //到了别的服务器去了
                                    Program.g_rabbitmq_comm.Send808Message(h, m_key, m.msgid, m.msgdm, m.msgaddtime);

                                    MustSendMsgSaveToRedis(r, mongodb, m.msgid, m.msgdm, m.msgaddtime);
                                    m.sendstatus = MustSendMsgData.SendStatus.SAVED;
                                    m.eventtime = DateTime.Now;
                                    rclist.Add(m_key + "_" + m.msgid.ToString() + "_" + m.msgflowid.ToString());
                                }
                            }
                        }
                    }
                    else if (m.sendstatus == MustSendMsgData.SendStatus.SENDING)
                    {
                        if ((DateTime.Now - m.eventtime).TotalSeconds > 60)
                        {
                            m.sendstatus = MustSendMsgData.SendStatus.SENDFAIL;
                            m.eventtime = DateTime.Now;
                        }
                    }
                    else if (m.sendstatus == MustSendMsgData.SendStatus.SENDED)
                    {
                        rclist.Add(m_key + "_" + m.msgid.ToString() + "_" + m.msgflowid.ToString());
                    }
                    else if (m.sendstatus == MustSendMsgData.SendStatus.SENDFAIL)
                    {
                        if ((DateTime.Now - m.msgaddtime).TotalHours > 48)
                        {
                            rclist.Add(m_key + "_" + m.msgid.ToString() + "_" + m.msgflowid.ToString());
                        }
                        else
                        {
                            if (m.sendcount < 4)
                            {
                                m.sendstatus = MustSendMsgData.SendStatus.WAIT;
                                m.eventtime = DateTime.Now;
                                string h = r.GetStringKey("h" + m_key);
                                if (h == Program.g_savedguid)
                                {
                                    //暂时离线
                                }
                                else
                                {
                                    //到了别的服务器去了
                                    Program.g_rabbitmq_comm.Send808Message(h, m_key, m.msgid, m.msgdm, m.msgaddtime);

                                    MustSendMsgSaveToRedis(r, mongodb, m.msgid, m.msgdm, m.msgaddtime);
                                    m.sendstatus = MustSendMsgData.SendStatus.SAVED;
                                    m.eventtime = DateTime.Now;
                                    rclist.Add(m_key + "_" + m.msgid.ToString() + "_" + m.msgflowid.ToString());
                                }
                            }
                            else
                            {
                                string h = r.GetStringKey("h" + m_key);
                                Program.g_rabbitmq_comm.Send808Message(h, m_key, m.msgid, m.msgdm, m.msgaddtime);

                                MustSendMsgSaveToRedis(r, mongodb, m.msgid, m.msgdm, m.msgaddtime);
                                m.sendstatus = MustSendMsgData.SendStatus.SAVED;
                                m.eventtime = DateTime.Now;
                                rclist.Add(m_key + "_" + m.msgid.ToString() + "_" + m.msgflowid.ToString());
                            }
                        }
                    }
                    else if (m.sendstatus == MustSendMsgData.SendStatus.SAVED)
                    {
                        rclist.Add(m_key + "_" + m.msgid.ToString() + "_" + m.msgflowid.ToString());
                    }
                }
                foreach (var m in rclist)
                {
                    m_mustsendmsgs.Remove(m);
                }
            }
        }
        if (isOnLine())
        {
            if ((DateTime.Now - loadfromredistime).TotalSeconds > 20)//轮询存储的待发送消息
            {
                loadfromredistime = DateTime.Now;
                MustSendMsgLoadFromRedis(r, mongodb);
            }
        }
        if (m_mustsendmsgs.Count > 0)
        {
            return m_mustsendmsgs.Count;//有待发送
        }
        else
        {

            if (isOnLine())
            {
                return 0;//在线，没有待发送
            }
            else
            {
                return -1;//既离线，又没有待发送
            }
        }
    }
